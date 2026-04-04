from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── POST /auth/register
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
@limiter.limit("30/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return auth_service.register(db, data)


# ── POST /auth/login
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login e obtenção de tokens",
)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login(db, data)


# ── POST /auth/refresh
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token com refresh token",
)
@limiter.limit("30/minute")
def refresh(
    request: Request, data: RefreshRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    return auth_service.refresh(db, data.refresh_token)
