
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.models.user import User

from app.schemas.user import (
    UserRegister,
    UserResponse,
    Token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# REGISTER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: UserRegister,
    db: Session = Depends(get_db)
):

    email = str(request.email).lower().strip()

    # Kiểm tra email đã tồn tại chưa
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Hash mật khẩu
    hashed_password = hash_password(request.password)

    # Tạo user mới
    user = User(
        full_name=request.full_name,
        email=email,
        hashed_password=hashed_password,
        role="customer"
    )

    # Lưu vào database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# LOGIN
@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    email = form_data.username.lower().strip()

    # Tìm user trong database
    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Kiểm tra tài khoản và mật khẩu
    if (
        user is None
        or not verify_password(
            form_data.password,
            user.hashed_password
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is inactive"
        )

    # Tạo JWT
    access_token = create_access_token(user.id)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )
