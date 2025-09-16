from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import os
from app.database import get_db
from app.models import UserProfile
from app.schemas import UserProfileOut, UserProfileUpdate
from app.config import AUTHORIZATION_KEY
from app.routers.user_auth import get_current_user_object

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# GET /profile/account_details
@router.get("/account_details", response_model=UserProfileOut)
async def get_my_profile(
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    return current_user

# PUT /profile/update_profile
@router.put("/update_profile", response_model=UserProfileOut)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user

# POST /profile/upload_photo
@router.post("/upload_photo", response_model=UserProfileOut)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    upload_dir = "app/static/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"user_{current_user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    current_user.photo_url = f"/static/profile_photos/user_{current_user.id}_{file.filename}"
    await db.commit()
    await db.refresh(current_user)
    return current_user

# DELETE /profile/remove_photo
@router.delete("/remove_photo", response_model=UserProfileOut)
async def remove_photo(
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    # Remove photo file from disk if exists
    if current_user.photo_url:
        file_path = current_user.photo_url.replace("/static/", "app/static/")
        if os.path.exists(file_path):
            os.remove(file_path)
        current_user.photo_url = None
        await db.commit()
        await db.refresh(current_user)
    return current_user
