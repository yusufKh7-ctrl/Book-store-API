from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from app.schemas.user import UserCreate
from app.models.user import User

from .auth_service import hash_password

async def create_user_service(user_data: UserCreate, db: AsyncSession):
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email alreay exist."
        )

    hashed_password = hash_password(user_data.password)
    db_user = User(
        name=user_data.name, email=user_data.email, hashed_password=hashed_password
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user
