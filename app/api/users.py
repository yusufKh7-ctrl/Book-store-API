from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import SessionDep
from ..schemas.user import UserCreate, UserPublic, UserLogin
from ..services.user_service import create_user_service
from ..services.auth_service import login_service
from app.core.dependencies import get_current_active_user
from typing import Annotated
router = APIRouter()


@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserCreate, db: SessionDep):
    return await create_user_service(user_data, db)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep
    ):
    user_login = UserLogin(
        email=form_data.username,
        password=form_data.password
    )
    return await login_service(user_login, db)

@router.get("/me", response_model=UserPublic)
async def get_me(user = Depends(get_current_active_user)):
    return user