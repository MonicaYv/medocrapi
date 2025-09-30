import os
import asyncio
from app.database import get_db
from app.schemas import UserProfileOut, UserProfileUpdate
from app.profile.user_auth import get_current_user_object, check_authorization_key
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile, File

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)

# GET /profile/account_details
@router.get("/account_details", response_model=UserProfileOut)
async def get_my_profile(
    current_user= Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    return UserProfileOut(
        id=profile.id,
        user_id=user.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        dob=profile.dob,
        gender=profile.gender,
        pan_number=profile.pan_number,
        profile_photo_path=profile.profile_photo_path,
        referral_code=profile.referral_code,
        email=user.email
    )

# PUT /profile/update_profile
@router.put("/update_profile", response_model=UserProfileOut)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    update_dict = profile_data.model_dump(exclude_unset=True)
    
    profile_fields = ['first_name', 'last_name', 'dob', 'gender', 'pan_number', 'age', 
                        'profile_photo_path', 'referral_code', 'address', 'city', 'state', 'pincode', 'country']
    for field in profile_fields:
        if field in update_dict:
            setattr(profile, field, update_dict[field])

    # Update User fields (notifications, quite_mode)
    user_fields = ['inapp_notifications', 'email_notifications', 'push_notifications',
                    'promotions_and_offers', 'quite_mode']
    for field in user_fields:
        if field in update_dict:
            setattr(user, field, update_dict[field])
            
    await db.commit()
    await db.refresh(profile)
    await db.refresh(user)

    return UserProfileOut(
        id=profile.id,
        user_id=user.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        dob=profile.dob,
        gender=profile.gender,
        pan_number=profile.pan_number,
        profile_photo_path=profile.profile_photo_path,
        referral_code=profile.referral_code,
        email=user.email
    )

# # POST /profile/upload_photo
@router.post("/upload_photo", response_model=UserProfileOut)
async def upload_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    upload_dir = "app/static/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"user_{user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    profile.profile_photo_path = f"/static/profile_photos/user_{user.id}_{file.filename}"
    await db.commit()
    await db.refresh(profile)
    await db.refresh(user)
    return UserProfileOut(
        id=profile.id,
        user_id=user.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        dob=profile.dob,
        gender=profile.gender,
        pan_number=profile.pan_number,
        profile_photo_path=profile.profile_photo_path,
        referral_code=profile.referral_code,
        email=user.email
    )

# # DELETE /profile/remove_photo
@router.delete("/remove_photo", response_model=UserProfileOut)
async def remove_photo(
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    # Remove photo file from disk if exists
    user, profile = current_user
    if profile.profile_photo_path:
        file_path = profile.profile_photo_path.replace("/static/", "app/static/")
        if await asyncio.to_thread(os.path.exists, file_path):
            await asyncio.to_thread(os.remove, file_path)
        profile.profile_photo_path = None
        await db.commit()
        await db.refresh(profile)
    return UserProfileOut(
        id=profile.id,
        user_id=user.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        dob=profile.dob,
        gender=profile.gender,
        pan_number=profile.pan_number,
        profile_photo_path=profile.profile_photo_path,
        referral_code=profile.referral_code,
        email=user.email
    )

# PUT /profile/update_photo
@router.put("/update_photo", response_model=UserProfileOut)
async def update_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    upload_dir = "app/static/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    if profile.profile_photo_path:
        old_file_path = profile.profile_photo_path.replace("/static/", "app/static/")
        if await asyncio.to_thread(os.path.exists, old_file_path):
            await asyncio.to_thread(os.remove, old_file_path)
    new_file_path = os.path.join(upload_dir, f"user_{user.id}_{file.filename}")
    
    with open(new_file_path, "wb") as f:
        f.write(await file.read())
    profile.profile_photo_path = f"/static/profile_photos/user_{user.id}_{file.filename}"
    await db.commit()
    await db.refresh(profile)
    await db.refresh(user)
    return UserProfileOut(
        id=profile.id,
        user_id=user.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        dob=profile.dob,
        gender=profile.gender,
        pan_number=profile.pan_number,
        profile_photo_path=profile.profile_photo_path,
        referral_code=profile.referral_code,
        email=user.email
    )
