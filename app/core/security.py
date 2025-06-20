from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

def create_access_token(sub: Dict[str, Any]) -> str:
    payload = sub.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expires_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
