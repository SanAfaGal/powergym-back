from datetime import datetime, timedelta, timezone
from app.utils.timezone import get_current_utc_datetime
from typing import Any, Union
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(
        subject: Union[str, Any],
        expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = get_current_utc_datetime() + expires_delta
    else:
        expire = get_current_utc_datetime() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
        subject: Union[str, Any],
        expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = get_current_utc_datetime() + expires_delta
    else:
        expire = get_current_utc_datetime() + timedelta(
            hours=settings.REFRESH_TOKEN_EXPIRE_HOURS
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None :
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        return None
