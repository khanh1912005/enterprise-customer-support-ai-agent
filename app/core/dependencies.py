
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User


# =====================================
# 1. OAUTH2 CONFIGURATION
# =====================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# =====================================
# 2. GET CURRENT AUTHENTICATED USER
# =====================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    # Phản hồi chung khi JWT không hợp lệ
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # =====================================
    # 2.1. VERIFY JWT
    # =====================================

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],

            # Bắt buộc hai claim quan trọng
            options={
                "require": ["sub", "exp"]
            }
        )

    except InvalidTokenError:

        raise credentials_exception

    # =====================================
    # 2.2. VALIDATE USER ID
    # =====================================

    subject = payload.get("sub")

    # Subject phải là chuỗi chứa chữ số ASCII
    if (
        not isinstance(subject, str)
        or not subject
        or not subject.isascii()
        or not subject.isdigit()
    ):

        raise credentials_exception

    try:

        user_id = int(subject)

    except ValueError:

        raise credentials_exception

    if user_id <= 0:

        raise credentials_exception

    # =====================================
    # 2.3. GET USER FROM DATABASE
    # =====================================

    user = db.get(User, user_id)

    # =====================================
    # 2.4. CHECK USER STATUS
    # =====================================

    if user is None or not user.is_active:

        raise credentials_exception

    # =====================================
    # 2.5. RETURN AUTHENTICATED USER
    # =====================================

    return user


# =====================================
# 3. SUPPORT STAFF AUTHORIZATION
# =====================================

def require_support_staff(
    current_user: User = Depends(get_current_user)
) -> User:

    allowed_roles = {
        "support_agent",
        "admin"
    }

    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission"
        )

    return current_user
