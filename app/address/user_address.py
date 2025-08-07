from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_db
from app.models import UserProfile, UserAddress
from app.schemas import UserAddressCreate, UserAddressOut, UserAddressUpdate
from app.config import AUTHORIZATION_KEY
from app.routers.user_auth import get_current_user_object

router = APIRouter(
    prefix="/address",
    tags=["User Address"]
)

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# Add a new address
@router.post("/add", response_model=UserAddressOut)
async def add_address(
    address_data: UserAddressCreate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    new_address = UserAddress(user_id=current_user.id, **address_data.dict())
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address

# Get all addresses for the current user
@router.get("/get", response_model=List[UserAddressOut])
async def get_addresses(
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    query = select(UserAddress).where(UserAddress.user_id == current_user.id)
    result = await db.execute(query)
    addresses = result.scalars().all()
    return addresses

# Update an address
@router.put("/update/{address_id}", response_model=UserAddressOut)
async def update_address(
    address_id: int,
    address_data: UserAddressUpdate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    query = select(UserAddress).where(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    )
    result = await db.execute(query)
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    for field, value in address_data.dict(exclude_unset=True).items():
        setattr(address, field, value)
    await db.commit()
    await db.refresh(address)
    return address

# Delete an address
@router.delete("/delete/{address_id}")
async def delete_address(
    address_id: int,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    query = select(UserAddress).where(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    )
    result = await db.execute(query)
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    await db.delete(address)
    await db.commit()
    return {"message": "Address deleted successfully"}
