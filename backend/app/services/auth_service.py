import uuid

from fastapi import HTTPException, status

from app.core.security import create_access_token, verify_password
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse


class AuthService:
    """Application service for authentication use cases."""

    def __init__(self, user_repository: SQLAlchemyUserRepository) -> None:
        self.user_repository = user_repository

    def login(self, payload: LoginRequest) -> TokenResponse:
        return self.login_by_credentials(
            username=payload.username,
            password=payload.password,
        )

    def login_by_credentials(self, username: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        token, expires_in = create_access_token(str(user.id), user.role)
        return TokenResponse(access_token=token, expires_in=expires_in)

    def get_current_user(self, user_id: str) -> CurrentUserResponse:
        try:
            normalized_user_id = str(uuid.UUID(user_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
            ) from exc

        user = self.user_repository.get_by_id(normalized_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User from token not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        return CurrentUserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )

    @staticmethod
    def ensure_role(current_user: CurrentUserResponse, allowed_roles: set[str]) -> None:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

