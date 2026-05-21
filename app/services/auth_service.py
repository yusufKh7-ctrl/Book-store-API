from typing import Annotated
from passlib.context import CryptContext
from fastapi import HTTPException, status,Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserLogin
from app.models.user import User
from typing import Dict
from app.repositories.user_repository import UserRepository
from app.db.session import SessionDep


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def login_service(
    data: UserLogin,
    db: AsyncSession 
) -> Dict[str, str]:
    repo = UserRepository(db)
    user =  await repo.get_user_by_email(data.email)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )
    
    token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }
    