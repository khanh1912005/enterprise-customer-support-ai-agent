
import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# Import Model để đăng ký các bảng với SQLAlchemy
from app.models.user import User
from app.models.ticket import Ticket


# Tạo SQLite database dùng riêng cho Testing
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def client():

    # Tạo bảng trong database test
    Base.metadata.create_all(bind=test_engine)

    # Thay database thật bằng database test
    def override_get_db():

        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Không dùng context manager ở đây vì lifespan hiện tại
    # của dự án sẽ kết nối PostgreSQL thật khi khởi động.
    test_client = TestClient(app)

    try:
        yield test_client

    finally:
        test_client.close()

        # Xóa dependency override
        app.dependency_overrides.clear()

        # Xóa các bảng test
        Base.metadata.drop_all(bind=test_engine)
