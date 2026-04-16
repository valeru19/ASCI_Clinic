import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.models.diagnosis import Diagnosis
from app.infrastructure.db.models.prescription import Prescription
from app.infrastructure.db.models.referral import Referral
from app.infrastructure.db.models.visit import Visit
from app.infrastructure.repositories.visit_repository import SQLAlchemyVisitRepository
from app.schemas.auth import CurrentUserResponse
from app.schemas.visits import (
    DiagnosesCreateRequest,
    DiagnosesCreateResponse,
    DiagnosisResponse,
    GenericCreateResult,
    PrescriptionsCreateRequest,
    ReferralResponse,
    ReferralsCreateRequest,
    ReferralsCreateResponse,
    VisitCompleteRequest,
    VisitCreateRequest,
    VisitListResponse,
    VisitResponse,
)


def _to_response(
    item: Visit,
    *,
    patient_id: str,
    patient_full_name: str,
    doctor_id: str,
    doctor_full_name: str,
) -> VisitResponse:
    return VisitResponse(
        id=str(item.id),
        appointment_id=str(item.appointment_id),
        patient_id=patient_id,
        patient_full_name=patient_full_name,
        doctor_id=doctor_id,
        doctor_full_name=doctor_full_name,
        chief_complaint=item.chief_complaint,
        exam_notes=item.exam_notes,
        treatment_plan=item.treatment_plan,
        visit_status=item.visit_status,
        closed_at=item.closed_at,
    )


class VisitService:
    """Application service for visit and diagnosis use cases."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SQLAlchemyVisitRepository(session)

    def _resolve_doctor_scope(self, current_user: CurrentUserResponse) -> str | None:
        if current_user.role != "doctor":
            return None
        doctor_id = self.repo.get_doctor_id_by_user_id(current_user.id)
        if not doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found for current user",
            )
        return doctor_id

    def create(
        self,
        payload: VisitCreateRequest,
        current_user: CurrentUserResponse,
    ) -> VisitResponse:
        appointment = self.repo.get_appointment(payload.appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )

        doctor_scope_id = self._resolve_doctor_scope(current_user)
        if doctor_scope_id and str(appointment.doctor_id) != doctor_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor can create visits only for own appointments",
            )

        existing = self.repo.get_by_appointment_id(payload.appointment_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Visit for appointment already exists",
            )

        if appointment.status in {"cancelled", "no_show"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Visit cannot be created for appointment in current status",
            )

        visit = Visit(
            appointment_id=uuid.UUID(payload.appointment_id),
            chief_complaint=payload.chief_complaint.strip(),
            exam_notes=payload.exam_notes.strip(),
            treatment_plan=payload.treatment_plan.strip() if payload.treatment_plan else None,
            visit_status="in_progress",
        )
        created = self.repo.create(visit)
        self.session.commit()
        patient_id = str(appointment.patient_id)
        doctor_id = str(appointment.doctor_id)
        return _to_response(
            created,
            patient_id=patient_id,
            patient_full_name=self.repo.get_patient_full_name(patient_id),
            doctor_id=doctor_id,
            doctor_full_name=self.repo.get_doctor_full_name(doctor_id),
        )

    def get_visit(self, visit_id: str, current_user: CurrentUserResponse) -> VisitResponse:
        visit = self.repo.get_by_id(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found",
            )

        appointment = self.repo.get_appointment(str(visit.appointment_id))
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment for visit not found",
            )

        doctor_scope_id = self._resolve_doctor_scope(current_user)
        if doctor_scope_id and str(appointment.doctor_id) != doctor_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor can view only own visits",
            )

        return _to_response(
            visit,
            patient_id=str(appointment.patient_id),
            patient_full_name=self.repo.get_patient_full_name(str(appointment.patient_id)),
            doctor_id=str(appointment.doctor_id),
            doctor_full_name=self.repo.get_doctor_full_name(str(appointment.doctor_id)),
        )

    def add_diagnoses(
        self,
        visit_id: str,
        payload: DiagnosesCreateRequest,
        current_user: CurrentUserResponse,
    ) -> DiagnosesCreateResponse:
        visit = self.repo.get_by_id(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found",
            )
        appointment = self.repo.get_appointment(str(visit.appointment_id))
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment for visit not found",
            )
        doctor_scope_id = self._resolve_doctor_scope(current_user)
        if doctor_scope_id:
            if str(appointment.doctor_id) != doctor_scope_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Doctor can assign diagnoses only for own patients",
                )
            if appointment.status != "completed" or visit.visit_status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Doctor can assign diagnoses only after completed appointment",
                )

        incoming_primary_count = sum(1 for item in payload.items if item.is_primary)
        if incoming_primary_count > 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only one primary diagnosis is allowed per request",
            )
        if incoming_primary_count > 0 and self.repo.count_primary_diagnoses(visit_id) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Primary diagnosis already exists for visit",
            )

        diagnosis_models: list[Diagnosis] = []
        for item in payload.items:
            icd10_code = item.icd10_code.upper()
            if not self.repo.icd10_code_exists(icd10_code):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ICD-10 code not found: {icd10_code}",
                )
            diagnosis_models.append(
                Diagnosis(
                    visit_id=uuid.UUID(visit_id),
                    icd10_code=icd10_code,
                    is_primary=item.is_primary,
                    comment=item.comment.strip() if item.comment else None,
                )
            )

        created_rows = self.repo.create_diagnoses(diagnosis_models)
        self.session.commit()

        return DiagnosesCreateResponse(
            visit_id=visit_id,
            created=len(created_rows),
            diagnoses=[
                DiagnosisResponse(
                    id=str(row.id),
                    icd10_code=row.icd10_code,
                    is_primary=row.is_primary,
                    comment=row.comment,
                )
                for row in created_rows
            ],
        )

    def add_prescriptions(
        self,
        visit_id: str,
        payload: PrescriptionsCreateRequest,
        current_user: CurrentUserResponse,
    ) -> GenericCreateResult:
        visit = self.repo.get_by_id(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found",
            )
        if visit.visit_status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Prescriptions can be added only to in-progress visit",
            )

        prescription_models: list[Prescription] = []
        for item in payload.items:
            if not self.repo.medication_exists(item.medication_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Medication not found: {item.medication_id}",
                )
            prescription_models.append(
                Prescription(
                    visit_id=uuid.UUID(visit_id),
                    medication_id=uuid.UUID(item.medication_id),
                    dosage=item.dosage.strip(),
                    frequency=item.frequency.strip(),
                    duration_days=item.duration_days,
                    instructions=item.instructions.strip() if item.instructions else None,
                )
            )

        created_rows = self.repo.create_prescriptions(prescription_models)
        self.session.commit()
        return GenericCreateResult(visit_id=visit_id, created=len(created_rows))

    def add_referrals(
        self,
        visit_id: str,
        payload: ReferralsCreateRequest,
        current_user: CurrentUserResponse,
    ) -> ReferralsCreateResponse:
        visit = self.repo.get_by_id(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found",
            )
        if visit.visit_status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Referrals can be added only to in-progress visit",
            )

        referral_models: list[Referral] = []
        for item in payload.items:
            if not self.repo.specialty_exists(item.target_specialty_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Specialty not found: {item.target_specialty_id}",
                )
            if item.target_doctor_id and not self.repo.doctor_exists(item.target_doctor_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Doctor not found: {item.target_doctor_id}",
                )
            referral_models.append(
                Referral(
                    visit_id=uuid.UUID(visit_id),
                    target_specialty_id=item.target_specialty_id,
                    target_doctor_id=uuid.UUID(item.target_doctor_id)
                    if item.target_doctor_id
                    else None,
                    reason=item.reason.strip(),
                    status="created",
                    comment=item.comment.strip() if item.comment else None,
                )
            )

        created_rows = self.repo.create_referrals(referral_models)
        self.session.commit()
        return ReferralsCreateResponse(
            visit_id=visit_id,
            created=len(created_rows),
            referrals=[
                ReferralResponse(
                    id=str(row.id),
                    target_specialty_id=row.target_specialty_id,
                    target_doctor_id=str(row.target_doctor_id)
                    if row.target_doctor_id
                    else None,
                    reason=row.reason,
                    status=row.status,
                    comment=row.comment,
                    created_at=row.created_at,
                )
                for row in created_rows
            ],
        )

    def list_visits(
        self,
        *,
        doctor_id: str | None,
        patient_id: str | None,
        visit_status: str | None,
        skip: int,
        limit: int,
        current_user: CurrentUserResponse,
    ) -> VisitListResponse:
        doctor_scope_id = self._resolve_doctor_scope(current_user)
        effective_doctor_id = doctor_scope_id or doctor_id

        total = self.repo.count_filtered(
            doctor_id=effective_doctor_id,
            patient_id=patient_id,
            visit_status=visit_status,
        )
        rows = self.repo.list_filtered(
            doctor_id=effective_doctor_id,
            patient_id=patient_id,
            visit_status=visit_status,
            skip=skip,
            limit=limit,
        )
        return VisitListResponse(
            items=[
                _to_response(
                    item,
                    patient_id=pid,
                    patient_full_name=self.repo.get_patient_full_name(pid),
                    doctor_id=did,
                    doctor_full_name=self.repo.get_doctor_full_name(did),
                )
                for item, pid, did in rows
            ],
            total=total,
        )

    def complete(
        self,
        visit_id: str,
        payload: VisitCompleteRequest,
        current_user: CurrentUserResponse,
    ) -> VisitResponse:
        visit = self.repo.get_by_id(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found",
            )

        appointment = self.repo.get_appointment(str(visit.appointment_id))
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment for visit not found",
            )

        doctor_scope_id = self._resolve_doctor_scope(current_user)
        if doctor_scope_id and str(appointment.doctor_id) != doctor_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor can complete only own visits",
            )

        if visit.visit_status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Visit cannot be completed in current status",
            )

        if payload.treatment_plan is not None:
            visit.treatment_plan = payload.treatment_plan.strip() or None
        visit.visit_status = "completed"
        visit.closed_at = datetime.now(UTC)

        if appointment.status not in {"completed", "cancelled", "no_show"}:
            appointment.status = "completed"
            appointment.updated_at = datetime.now(UTC)
            self.session.add(appointment)

        self.session.add(visit)
        self.session.commit()
        self.session.refresh(visit)

        return _to_response(
            visit,
            patient_id=str(appointment.patient_id),
            patient_full_name=self.repo.get_patient_full_name(str(appointment.patient_id)),
            doctor_id=str(appointment.doctor_id),
            doctor_full_name=self.repo.get_doctor_full_name(str(appointment.doctor_id)),
        )

