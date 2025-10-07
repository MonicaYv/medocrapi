from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.profile.user_auth import get_current_user_object, check_authorization_key
from app.schemas import NotificationSettingsOut, NotificationSettingsUpdate
from app.models import SavedLocation, SearchHistory

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


# GET /notifications/get_notification
@router.get("/get_notification", response_model=NotificationSettingsOut)
async def get_notification(
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user

    return NotificationSettingsOut(
        inapp_notifications=user.inapp_notifications,
        email_notifications=user.email_notifications,
        push_notifications=user.push_notifications,
        regulatory_alerts=user.regulatory_alerts,
        promotions_and_offers=user.promotions_and_offers,
        payment_notifications=profile.payment_notifications,
        location_notification=profile.location_notification,
        quite_mode=user.quite_mode,
        quite_mode_start_time=user.quite_mode_start_time,
        quite_mode_end_time=user.quite_mode_end_time
    )

# PUT /notifications/update_notification
@router.put("/update_notification", response_model=NotificationSettingsOut)
async def update_notification(
    settings: NotificationSettingsUpdate,
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    update_dict = settings.model_dump(exclude_unset=True)

    # Fields belonging to User
    user_fields = [
        "inapp_notifications",
        "email_notifications",
        "push_notifications",
        "regulatory_alerts",
        "promotions_and_offers",
        "quite_mode",
        "quite_mode_start_time",
        "quite_mode_end_time"
    ]

    # Fields belonging to UserProfile
    profile_fields = [
        "payment_notifications",
        "location_notification"
    ]

    for field in user_fields:
        if field in update_dict:
            setattr(user, field if field != "inapp_notifications" else "inapp_notifications", update_dict[field])

    for field in profile_fields:
        if field in update_dict:
            setattr(profile, field, update_dict[field])

    await db.commit()
    await db.refresh(user)
    await db.refresh(profile)

    return NotificationSettingsOut(
        inapp_notifications=user.inapp_notifications,
        email_notifications=user.email_notifications,
        push_notifications=user.push_notifications,
        regulatory_alerts=user.regulatory_alerts,
        promotions_and_offers=user.promotions_and_offers,
        payment_notifications=profile.payment_notifications,
        location_notification=profile.location_notification,
        quite_mode=user.quite_mode,
        quite_mode_start_time=user.quite_mode_start_time,
        quite_mode_end_time=user.quite_mode_end_time
    )
    
# DELETE /data-management/delete_account
@router.delete("/delete_account")
async def delete_account(
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account already deactivated")

    user.is_active = False
    db.add(user)
    await db.commit()
    return {"message": "Account deactivated successfully."}


# DELETE /data-management/clear_data
@router.delete("/clear_data")
async def clear_data(
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user

    # Delete related data (cascades may already clean some)
    await db.execute(SavedLocation.__table__.delete().where(SavedLocation.user_id == user.id))
    await db.execute(SearchHistory.__table__.delete().where(SearchHistory.user_id == user.id))
    # TODO - Implement full functionality
    # await db.execute(Donation.__table__.delete().where(Donation.user_id == user.id))
    # await db.execute(CouponHistory.__table__.delete().where(CouponHistory.user_id == user.id))
    # await db.execute(Coupon.__table__.delete().where(Coupon.advertiser_id == user.id))
    # await db.execute(RewardHistory.__table__.delete().where(RewardHistory.user_id == user.id))

    await db.commit()
    return {"message": "All user-related data cleared successfully."}


# DELETE /data-management/clear_search_history
@router.delete("/clear_search_history")
async def clear_search_history(
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user

    # Delete all search history for the user
    await db.execute(SearchHistory.__table__.delete().where(SearchHistory.user_id == user.id))
    # TODO - Implement any future history tables
    await db.commit()

    return {"message": "All search history cleared successfully."}
