from fastapi import APIRouter, Depends
from app.db.session import SessionDep
from app.services.order_service import create_order_service, get_order_by_id_service
from app.schemas.order import OrderPublic,OrderCreate
from app.core.dependencies import get_current_active_user

router = APIRouter()

@router.post("/", response_model=OrderPublic)
async def create_order(
    db: SessionDep,
    order_data: OrderCreate,
    current_user = Depends(get_current_active_user)
    ):
    return await create_order_service(db, order_data, current_user)

@router.get("/{order_id}", response_model=OrderPublic)
async def get_order_by_id(db: SessionDep, order_id: int):
    return await get_order_by_id_service(db, order_id)