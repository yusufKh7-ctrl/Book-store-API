from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.repositories.user_repository import UserRepository
from .auth_service import create_access_token, hash_password, verify_password


async def create_user_service(user_data: UserCreate, db: AsyncSession):
    repo = UserRepository(db)
    existing_user = await repo.get_user_by_email(user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email alreay exist."
        )

    hashed_password = hash_password(user_data.password)
    db_user = User(
        name=user_data.name, email=user_data.email, hashed_password=hashed_password
    )

    repo.add_user(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def login_service(data: UserLogin, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_email(data.email)

    if not user:
        raise HTTPException(400, "Invalid credintials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(400, "Invalid credintials")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


async def get_user_by_id_service(user_id: int, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
        
    return user