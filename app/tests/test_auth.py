import pytest
from fastapi import HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import create_user_service
from app.services.auth_service import (
    verify_password,
    create_access_token,
    login_service,
)

from jose import jwt
from app.config import settings


@pytest.mark.asyncio
async def test_hash_password(db_session):
    user_data = UserCreate(
        name="test user",
        email="testuser@gmail.com",
        password="testuser123"
    )
    user = await create_user_service(user_data, db_session)

    assert user.hashed_password != user_data.password

    assert verify_password(user_data.password, user.hashed_password) is True
    assert verify_password("wrongPassword", user.hashed_password) is False


def test_create_access_token():
    data = {"sub": "42"}
    token = create_access_token(data)
    
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded["sub"] == "42"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_login_service(db_session):
    user_data = UserCreate(
        name="test user",
        email="testuser@gmail.com",
        password="testuser123"
    )
    user = await create_user_service(user_data, db_session)

    login_data = UserLogin(
        email=user.email,
        password=user_data.password
    )
    result = await login_service(login_data, db_session)

    decode = jwt.decode(result["access_token"], settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    

    assert "access_token" in result
    assert "token_type" in result

    assert decode["sub"] == str(user.id)
    assert isinstance(result["access_token"], str)
    assert len(result["access_token"]) > 0
    assert isinstance(result["token_type"], str)
    assert result["token_type"] == "bearer"



@pytest.mark.asyncio
async def test_login_wrong_password(db_session):
    user_data = UserCreate(
        name="test user",
        email="testuser@gmail.com",
        password="testuser123"
    )
    user = await create_user_service(user_data, db_session)
    
    login_data = UserLogin(
        email=user.email,
        password="wrongPassword"
    )

    with pytest.raises(HTTPException) as exc_info:
        await login_service(login_data, db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password."


@pytest.mark.asyncio
async def test_login_user_not_found(db_session):
    login_data = UserLogin(
        email="notfounduser@gmail.com",
        password="Iamnothere"
    )
    with pytest.raises(HTTPException) as exc_info:
        await login_service(login_data, db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password."