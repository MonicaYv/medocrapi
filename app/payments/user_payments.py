from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import PaymentMethod
from app.schemas import PaymentMethodCreate, PaymentMethodOut, PaymentMethodUpdate
from app.profile.user_auth import get_current_user_object, check_authorization_key

router = APIRouter(
    prefix="/payments",
    tags=["Payment Methods"]
)

# Add a new payment method
@router.post("/add_payment_method", response_model=PaymentMethodOut)
async def add_payment_method(
    payment_data: PaymentMethodCreate,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    try:
        existing_card = await db.execute(
            select(PaymentMethod).where(
                PaymentMethod.user_id == user.id,
                PaymentMethod.card_number_masked == payment_data.card_number_masked
            )
        )
        if existing_card.scalars().first():
            raise HTTPException(status_code=409, detail="This card is already added")

        new_payment_method = PaymentMethod(
            user_id=user.id,
            card_holder_name=payment_data.card_holder_name,
            card_number_masked=payment_data.card_number_masked,
            card_type=payment_data.card_type,
            expiry_month=payment_data.expiry_month,
            expiry_year=payment_data.expiry_year,
            is_default=payment_data.is_default,
            payment_gateway=payment_data.payment_gateway or "stripe",
            status="active"
        )

        # If this is set as default, make other cards non-default
        if payment_data.is_default:
            await db.execute(
                update(PaymentMethod).where(
                    PaymentMethod.user_id == user.id
                ).values(is_default=False)
            )

        db.add(new_payment_method)
        await db.commit()
        await db.refresh(new_payment_method)
        return new_payment_method
    except Exception as e:
        await db.rollback()
        print(f"Error adding payment method: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add payment method: {str(e)}")

# Get all payment methods for the current user
@router.get("/get_payment_methods", response_model=List[PaymentMethodOut])
async def get_payment_methods(
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    query = select(PaymentMethod).where(
        PaymentMethod.user_id == user.id,
        PaymentMethod.status == "active"
    ).order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
    result = await db.execute(query)
    payment_methods = result.scalars().all()
    return payment_methods

# Update a payment method
@router.put("/update_payment_method/{payment_method_id}", response_model=PaymentMethodOut)
async def update_payment_method(
    payment_method_id: int,
    payment_data: PaymentMethodUpdate,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    try:
        query = select(PaymentMethod).where(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.user_id == user.id,
            PaymentMethod.status == "active"
        )
        result = await db.execute(query)
        payment_method = result.scalars().first()
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")

        if payment_data.card_holder_name is not None:
            payment_method.card_holder_name = payment_data.card_holder_name
        if payment_data.expiry_month is not None:
            payment_method.expiry_month = payment_data.expiry_month
        if payment_data.expiry_year is not None:
            payment_method.expiry_year = payment_data.expiry_year
        if payment_data.is_default is not None:
            if payment_data.is_default:
                await db.execute(
                    update(PaymentMethod).where(
                        PaymentMethod.user_id == user.id,
                        PaymentMethod.id != payment_method_id
                    ).values(is_default=False)
                )
            payment_method.is_default = payment_data.is_default

        payment_method.updated_at = datetime.now()
        await db.commit()
        await db.refresh(payment_method)
        return payment_method
    except Exception as e:
        await db.rollback()
        print(f"Error updating payment method: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update payment method: {str(e)}")

# Delete (deactivate) a payment method
@router.delete("/delete_payment_method/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: int,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    try:
        query = select(PaymentMethod).where(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.user_id == user.id,
            PaymentMethod.status == "active"
        )
        result = await db.execute(query)
        payment_method = result.scalars().first()
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")

        payment_method.status = "deleted"
        payment_method.updated_at = datetime.now()
        await db.commit()
        return {"message": "Payment method deleted successfully"}
    except Exception as e:
        await db.rollback()
        print(f"Error deleting payment method: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete payment method: {str(e)}")

# Set a payment method as default
@router.put("/set_default_payment_method/{payment_method_id}")
async def set_default_payment_method(
    payment_method_id: int,
    current_user = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    try:
        query = select(PaymentMethod).where(
            PaymentMethod.id == payment_method_id,
            PaymentMethod.user_id == user.id,
        )
        result = await db.execute(query)
        payment_method = result.scalars().first()
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")

        await db.execute(
            update(PaymentMethod).where(
                PaymentMethod.user_id == user.id,
                PaymentMethod.id != payment_method_id
            ).values(is_default=False)
        )
        payment_method.is_default = True
        payment_method.updated_at = datetime.now()
        await db.commit()
        return {"message": "Payment method set as default successfully"}
    except Exception as e:
        await db.rollback()
        print(f"Error setting default payment method: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set default payment method: {str(e)}")
