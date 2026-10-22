from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Order, User


async def set_user(
    session: AsyncSession,
    tg_id: int,
    full_name: str,
    username: str | None = None,
) -> User:
    stmt = insert(User).values(
        tg_id=tg_id,
        full_name=full_name,
        username=username,
    )
    
    stmt = stmt.on_conflict_do_update(
        index_elements=["tg_id"],
        set_={
            "full_name": stmt.excluded.full_name,
            "username": stmt.excluded.username,
        },
    )
    
    await session.execute(stmt)
    await session.commit()
    
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one()


async def create_order(
    session: AsyncSession,
    user_id: int,
    service_type: str,
    description: str,
    photo_file_id: str | None = None,
) -> Order:
    order = Order(
        user_id=user_id,
        service_type=service_type,
        description=description,
        photo_file_id=photo_file_id,
        status="NEW",
    )
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    return order


async def update_order_status(
    session: AsyncSession,
    order_id: int,
    new_status: str,
) -> bool:
    result = await session.execute(select(Order).where(Order.id == order_id))
    
    if not (order := result.scalar_one_or_none()):
        return False
    
    order.status = new_status
    await session.commit()
    return True


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.user))
    )
    return result.scalar_one_or_none()
