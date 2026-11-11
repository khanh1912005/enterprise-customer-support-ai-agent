
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Đọc cấu hình từ file .env
load_dotenv()

# Lấy thông tin kết nối
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)

# Tạo kết nối đến PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Tạo cơ chế quản lý phiên làm việc
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Lớp gốc cho các model database
class Base(DeclarativeBase):
    pass


# Cấp database session cho API
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
