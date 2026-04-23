import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.logging_config import configure_logging
from app.core.settings import settings

configure_logging()
logger = logging.getLogger("ais_clinic.api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AIS Clinic API",
        version="0.2.0",
        description="Слоистый backend-каркас для АИС 'Клиника'.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_origin_regex=settings.cors_allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        response.headers["X-Request-ID"] = request_id
        if response.status_code >= 400:
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": request.url.query,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None,
                },
            )
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", "-")
        logger.warning(
            "HTTP exception",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": request.url.query,
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": request_id},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        request_id = getattr(request.state, "request_id", "-")
        logger.warning(
            "Validation error",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": request.url.query,
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "request_id": request_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "-")
        logger.exception(
            "Unhandled application exception",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": request.url.query,
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
                "error_type": type(exc).__name__,
            },
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
