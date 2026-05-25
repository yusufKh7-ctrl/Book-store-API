from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserUpdate
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


async def get_all_users_service(db: AsyncSession):
    repo = UserRepository(db)
    users = await repo.get_all_users()
    return users


async def get_user_by_id_service(user_id: int, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return user


async def update_user_service(user_id: int, user_data: UserUpdate, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    update_user = user_data.model_dump(exclude_unset=True)

    for key, value in update_user.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_service(user_id: int, db: AsyncSession, current_user: User):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have permission to delete this user",
        )

    await repo.delete_user(user_id)
    await db.commit()
