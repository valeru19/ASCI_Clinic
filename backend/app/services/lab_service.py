import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.models.lab import LabOrder, LabOrderItem, LabResult
from app.infrastructure.repositories.lab_repository import SQLAlchemyLabRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.labs import (
    LabOrderCreateRequest,
    LabOrderItemResponse,
    LabOrderItemsCreateRequest,
    LabOrderItemsCreateResponse,
    LabOrderResponse,
    LabResultCreateRequest,
    LabResultListResponse,
    LabResultResponse,
)


class LabService:
    """Application service for laboratory use cases."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SQLAlchemyLabRepository(session)

    def create_order(
        self,
        payload: LabOrderCreateRequest,
        current_user: CurrentUserResponse,
    ) -> LabOrderResponse:
        context = self.repo.visit_context(payload.visit_id)
        if not context:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")
        patient_id, doctor_id = context
        order = LabOrder(
            visit_id=uuid.UUID(payload.visit_id),
            patient_id=uuid.UUID(patient_id),
            ordered_by_doctor_id=uuid.UUID(doctor_id),
            status="created",
        )
        created = self.repo.create_order(order)
        self.session.commit()
        return LabOrderResponse(
            id=str(created.id),
            visit_id=str(created.visit_id),
            patient_id=str(created.patient_id),
            ordered_by_doctor_id=str(created.ordered_by_doctor_id),
            status=created.status,
            ordered_at=created.ordered_at,
        )

    def add_order_items(
        self,
        order_id: str,
        payload: LabOrderItemsCreateRequest,
        current_user: CurrentUserResponse,
    ) -> LabOrderItemsCreateResponse:
        order = self.repo.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab order not found",
            )
        if order.status in {"completed", "cancelled"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot add items to closed lab order",
            )

        items: list[LabOrderItem] = []
        for item in payload.items:
            if not self.repo.test_type_exists(item.test_type_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lab test type not found: {item.test_type_id}",
                )
            items.append(
                LabOrderItem(
                    lab_order_id=uuid.UUID(order_id),
                    test_type_id=uuid.UUID(item.test_type_id),
                    priority=item.priority,
                )
            )
        created = self.repo.create_order_items(items)
        if order.status == "created":
            order.status = "in_progress"
            self.session.add(order)
        self.session.commit()
        return LabOrderItemsCreateResponse(
            lab_order_id=order_id,
            created=len(created),
            items=[
                LabOrderItemResponse(
                    id=str(item.id),
                    lab_order_id=str(item.lab_order_id),
                    test_type_id=str(item.test_type_id),
                    priority=item.priority,
                )
                for item in created
            ],
        )

    def create_result(
        self,
        payload: LabResultCreateRequest,
        current_user: CurrentUserResponse,
    ) -> LabResultResponse:
        item = self.repo.get_order_item(payload.lab_order_item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab order item not found",
            )
        if self.repo.has_result_for_order_item(payload.lab_order_item_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Result for lab order item already exists",
            )
        if not self.repo.doctor_exists(payload.validated_by_doctor_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found",
            )
        order = self.repo.get_order(str(item.lab_order_id))
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab order not found",
            )
        result = LabResult(
            lab_order_item_id=uuid.UUID(payload.lab_order_item_id),
            value_text=payload.value_text.strip() if payload.value_text else None,
            value_numeric=Decimal(str(payload.value_numeric))
            if payload.value_numeric is not None
            else None,
            unit=payload.unit.strip() if payload.unit else None,
            reference_range=payload.reference_range.strip() if payload.reference_range else None,
            flag=payload.flag,
            validated_by_doctor_id=uuid.UUID(payload.validated_by_doctor_id),
        )
        created = self.repo.create_result(result)
        if order.status != "completed":
            order.status = "completed"
            self.session.add(order)
        self.session.commit()
        return LabResultResponse(
            id=str(created.id),
            lab_order_item_id=str(created.lab_order_item_id),
            lab_order_id=str(order.id),
            patient_id=str(order.patient_id),
            value_text=created.value_text,
            value_numeric=float(created.value_numeric) if created.value_numeric is not None else None,
            unit=created.unit,
            reference_range=created.reference_range,
            flag=created.flag,
            resulted_at=created.resulted_at,
            validated_by_doctor_id=str(created.validated_by_doctor_id)
            if created.validated_by_doctor_id
            else None,
        )

    def list_results(
        self,
        *,
        patient_id: str | None,
        order_id: str | None,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> LabResultListResponse:
        total = self.repo.count_results(patient_id=patient_id, order_id=order_id)
        rows = self.repo.list_results(
            patient_id=patient_id,
            order_id=order_id,
            skip=skip,
            limit=limit,
        )
        return LabResultListResponse(
            items=[
                LabResultResponse(
                    id=str(result.id),
                    lab_order_item_id=str(result.lab_order_item_id),
                    lab_order_id=lab_order_id,
                    patient_id=row_patient_id,
                    value_text=result.value_text,
                    value_numeric=float(result.value_numeric)
                    if result.value_numeric is not None
                    else None,
                    unit=result.unit,
                    reference_range=result.reference_range,
                    flag=result.flag,
                    resulted_at=result.resulted_at,
                    validated_by_doctor_id=str(result.validated_by_doctor_id)
                    if result.validated_by_doctor_id
                    else None,
                )
                for result, lab_order_id, row_patient_id in rows
            ],
            total=total,
        )

