from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.models import CartItem
from app.schemas import CartItemCreate, CartItemUpdate, CartItemOut
from app.profile.user_auth import get_current_user_object

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

@router.post("/add", response_model=CartItemOut)
async def cart_list_add(
    cart_item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object) 
):
    user, profile = current_user_data

    medicine_id_str = str(cart_item.medicine_id)
    
    new_item = CartItem(
        **cart_item.dict(exclude={"medicine_id"}),
        medicine_id=medicine_id_str,
        user_id=user.id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.put("/update/{item_id}", response_model=CartItemOut)
async def cart_list_update(
    item_id: int,
    cart_item: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object)
):
    user, profile = current_user_data
    query = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user.id)
    )
    item = query.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    for key, value in cart_item.dict(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/remove/{item_id}", response_model=dict)
async def cart_list_remove(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object)
):
    user, profile = current_user_data
    query = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user.id)
    )
    item = query.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await db.delete(item)
    await db.commit()
    return {"detail": "Cart item removed successfully"}

@router.get("/list/", response_model=List[CartItemOut])
async def cart_list(
    db: AsyncSession = Depends(get_db),
    current_user_data: tuple = Depends(get_current_user_object)
):
    user, profile = current_user_data
    query = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    items = query.scalars().all()
    return items
