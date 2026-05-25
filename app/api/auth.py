from fastapi import Depends
from fastapi.routing import APIRouter
from ..schemas.user import UserLogin
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import SessionDep
from ..services.auth_service import login_service
from typing import Annotated

router = APIRouter()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep
):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return await login_service(user_login, db)
