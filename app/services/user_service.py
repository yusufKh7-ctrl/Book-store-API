from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.repositories.user_repository import UserRepository
from .auth_service import create_access_token, hash_password, verify_password
from app.core.logger import get_logger

logger = get_logger(__name__)

async def create_user_service(user_data: UserCreate, db: AsyncSession):
    repo = UserRepository(db)
    existing_user = await repo.get_user_by_email(user_data.email)

    if existing_user:
        logger.warning(f"Registration failed: email already exists ({user_data.email})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists."
        )   

    hashed_password = hash_password(user_data.password)
    db_user = User(
        name=user_data.name, email=user_data.email, hashed_password=hashed_password
    )

    repo.add_user(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"User created: user_name={user_data.name}, user_email={user_data.email}")
    return db_user


async def get_all_users_service(db: AsyncSession, skip: int = 0, limit: int = 10):
    repo = UserRepository(db)
    users = await repo.get_all_users(skip, limit)
    return users


async def get_user_by_id_service(user_id: int, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        logger.warning(f"User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return user


async def update_user_service(user_id: int, user_data: UserUpdate, db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)

    if not user:
        logger.warning(f"Update user not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    update_user = user_data.model_dump(exclude_unset=True)

    for key, value in update_user.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    logger.info(f"User updated: user_id={user_id}")
    return user


async def delete_user_service(user_id: int, db: AsyncSession, current_user: User):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Delete user not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if current_user.id != user_id and not current_user.is_admin:
        logger.warning(f"Permission denied: user_id={current_user.id} tried to delete user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this user",
        )

    await repo.delete_user(user_id)
    await db.commit()
    logger.info(f"User deleted: user_id={user_id}, by_user_id={current_user.id}")
