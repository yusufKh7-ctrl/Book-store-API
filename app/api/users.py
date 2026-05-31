from fastapi import APIRouter, Depends, status
from app.db.session import SessionDep
from ..schemas.user import UserCreate, UserPublic, UserUpdate
from ..services.user_service import (
    create_user_service,
    get_user_by_id_service,
    update_user_service,
    delete_user_service,
    get_all_users_service,
)
from app.core.dependencies import get_current_active_user, get_admin_user

router = APIRouter()


@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserCreate, db: SessionDep):
    return await create_user_service(user_data, db)


@router.get("/me", response_model=UserPublic)
async def get_me(user=Depends(get_current_active_user)):
    return user


@router.get("/", response_model=list[UserPublic])
async def get_users(db: SessionDep, current_user=Depends(get_admin_user)):
    return await get_all_users_service(db)


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(user_id: int, db: SessionDep):
    return await get_user_by_id_service(user_id, db)


@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: SessionDep,
    current_user=Depends(get_current_active_user),
):
    return await update_user_service(user_id, user_data, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, db: SessionDep, current_user=Depends(get_current_active_user)
):
    return await delete_user_service(user_id, db, current_user)
