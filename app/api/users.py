from fastapi import APIRouter, Depends
from app.db.session import SessionDep
from ..schemas.user import UserCreate, UserPublic
from ..services.user_service import create_user_service
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserCreate, db: SessionDep):
    return await create_user_service(user_data, db)

@router.get("/me", response_model=UserPublic)
async def get_me(user = Depends(get_current_active_user)):
    return user