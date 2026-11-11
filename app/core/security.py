
import os

from datetime import datetime, timedelta, timezone

import jwt

from dotenv import load_dotenv
from pwdlib import PasswordHash


# Đọc biến môi trường
load_dotenv()

# Lấy SECRET_KEY từ file .env
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing in .env")


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Khởi tạo công cụ hash mật khẩu
password_hash = PasswordHash.recommended()


# Hash mật khẩu
def hash_password(password: str) -> str:

    return password_hash.hash(password)


# Kiểm tra mật khẩu
def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        password,
        hashed_password
    )


# Tạo JWT
def create_access_token(user_id: int) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token
