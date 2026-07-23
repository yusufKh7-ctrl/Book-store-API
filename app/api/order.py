from fastapi import APIRouter, Depends, status, Request
from app.db.session import SessionDep
from app.services.order_service import (
    create_order_service,
    get_order_by_id_service,
    get_all_orders_service,
    delete_order_by_id_service,
    update_order_service,
)
from app.schemas.order import OrderPublic, OrderCreate, OrderUpdate
from app.core.dependencies import get_current_active_user, get_admin_user
from app.core.limiter import limiter

router = APIRouter()


@router.post("/", response_model=OrderPublic)
@limiter.limit("3/minute")
async def create_order(
    request: Request,
    db: SessionDep,
    order_data: OrderCreate,
    current_user=Depends(get_current_active_user),
):
    return await create_order_service(db, order_data, current_user)


@router.get("/{order_id}", response_model=OrderPublic)
async def get_order_by_id(db: SessionDep, order_id: int):
    return await get_order_by_id_service(db, order_id)


@router.get("/", response_model=list[OrderPublic])
async def get_all_orders(
    db: SessionDep, current_user=Depends(get_admin_user), skip: int = 0, limit: int = 10
):
    return await get_all_orders_service(db, skip, limit)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    db: SessionDep, order_id: int, current_user=Depends(get_current_active_user)
):
    await delete_order_by_id_service(db, order_id, current_user)


@router.put("/{order_id}", response_model=OrderPublic)
async def update_order(
    db: SessionDep,
    order_id: int,
    order_data: OrderUpdate,
    current_user=Depends(get_current_active_user),
):
    return await update_order_service(db, order_id, order_data, current_user)
