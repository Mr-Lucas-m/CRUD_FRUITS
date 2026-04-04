import structlog
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.repositories import user_repository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse

logger = structlog.get_logger()


def register(db: Session, data: UserCreate) -> UserResponse:
    if user_repository.get_user_by_email(db, data.email):
        raise EmailAlreadyRegisteredError(data.email)
    hashed = hash_password(data.password)
    user = user_repository.create_user(db, data.email, hashed)
    logger.info("user_registered", user_id=user.id, email=user.email)
    return UserResponse.model_validate(user)


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_repository.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError()
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    logger.info("user_logged_in", user_id=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def refresh(db: Session, refresh_token: str) -> TokenResponse:
    from fastapi import HTTPException, status

    payload = verify_token(refresh_token, "refresh")
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_repository.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.id})
    new_refresh = create_refresh_token({"sub": user.id})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)
