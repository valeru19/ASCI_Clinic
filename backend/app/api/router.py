from fastapi import APIRouter

from app.api.v1.appointments import router as appointments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.labs import router as labs_router
from app.api.v1.patients import router as patients_router
from app.api.v1.reports import router as reports_router
from app.api.v1.schedule_exceptions import router as schedule_exceptions_router
from app.api.v1.schedule_slots import router as schedule_slots_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.specialties import router as specialties_router
from app.api.v1.visits import router as visits_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(doctors_router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(specialties_router, prefix="/specialties", tags=["Doctors"])
api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])
api_router.include_router(schedules_router, prefix="/schedules", tags=["Schedules"])
api_router.include_router(schedule_slots_router, prefix="/schedule-slots", tags=["Schedules"])
api_router.include_router(
    schedule_exceptions_router,
    prefix="/schedule-exceptions",
    tags=["Schedules"],
)
api_router.include_router(appointments_router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(visits_router, prefix="/visits", tags=["Visits"])
api_router.include_router(labs_router, prefix="/labs", tags=["Labs"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
