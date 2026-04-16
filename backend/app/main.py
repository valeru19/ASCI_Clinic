from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="AIS Clinic API",
        version="0.2.0",
        description="Слоистый backend-каркас для АИС 'Клиника'.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/", tags=["System"])
    def root() -> dict[str, str]:
        return {"message": "AIS Clinic API is running"}

    @app.get("/health", tags=["System"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
