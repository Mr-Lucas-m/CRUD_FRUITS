import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.main import app
from app.models import category, fruit, stock_movement, user  # noqa: F401 — registra todos os models

engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine_test, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client(setup_db):
    def override_get_db():
        session = TestingSession()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def override_get_current_user():
        from app.models.user import User

        return User(
            id="test-user-id",
            email="test@test.com",
            hashed_password="hashed",
            is_active=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
