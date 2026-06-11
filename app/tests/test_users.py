import pytest
from fastapi import HTTPException
from app.schemas.user import UserCreate
from app.services.user_service import (
    create_user_service,
    get_user_by_id_service,
    delete_user_service
)


@pytest.mark.asyncio
async def test_create_user_success(db_session):
    user_data = UserCreate(
        name="Test user", email="testuser@example.com", password="testpassword123"
    )
    user = await create_user_service(user_data, db_session)
    assert user.id is not None
    assert user.name == user_data.name
    assert user.email == user_data.email


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session):
    user_data = UserCreate(
        name="Test user", email="testuser@example.com", password="testpassword123"
    )
    await create_user_service(user_data, db_session)
    with pytest.raises(HTTPException) as exc_info:
        await create_user_service(user_data, db_session)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already exists."


@pytest.mark.asyncio
async def test_get_user_by_id_success(db_session, normal_user):
    user = await get_user_by_id_service(normal_user.id, db_session)
    assert user.id == normal_user.id
    assert user.name == normal_user.name
    assert user.email == normal_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_user_by_id_service(999, db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found."


@pytest.mark.asyncio
async def test_admin_can_delete_any_user(db_session, admin_user, normal_user):
    await delete_user_service(normal_user.id, db_session, admin_user)
    with pytest.raises(HTTPException) as exc_info:
        await get_user_by_id_service(normal_user.id, db_session)
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_success(db_session, normal_user):
    await delete_user_service(normal_user.id, db_session, normal_user)
    with pytest.raises(HTTPException) as exc_info:
        await get_user_by_id_service(normal_user.id, db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found."


@pytest.mark.asyncio
async def test_delete_user_unauthorized(db_session, normal_user):
    user_data = UserCreate(
        name="Test delete", email="testdelete@example.com", password="deletepassword123"
    )
    user = await create_user_service(user_data, db_session)

    with pytest.raises(HTTPException) as exc_info:
        await delete_user_service(user.id, db_session, normal_user)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "You don't have permission to delete this user"
