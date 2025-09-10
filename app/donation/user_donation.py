from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, update, delete
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.config import AUTHORIZATION_KEY
from app.models import DonationTypes as DonationTypesModel, UserProfile, Donation, DonationPost
from app.schemas import DonationTypes, DonationOut, DonationHistoryFilter, DonationBillOut
from app.routers.user_auth import get_current_user_object


router = APIRouter( 
    prefix="/donation",
    tags=["donation"]
)

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

 # =========== Donation APIs ===========

@router.get("/donation_types", response_model=List[DonationTypes])
async def get_donation_types(
    db: AsyncSession = Depends(get_db), 
    _auth=Depends(check_authorization_key),
    current_user: UserProfile = Depends(get_current_user_object)
):
    try:
        query = select(DonationTypesModel).where(DonationTypesModel.is_active == True)
        result = await db.execute(query)
        donation_types = result.scalars().all()
        return donation_types
    except Exception as e:
        print(f"Error getting donation types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get donation types: {str(e)}")

@router.get("/donation_history", response_model=List[DonationOut])
async def get_donation_history(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user: UserProfile = Depends(get_current_user_object),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    start_date: Optional[datetime] = Query(None, description="Filter from start date"),
    end_date: Optional[datetime] = Query(None, description="Filter until end date"),
    min_amount: Optional[int] = Query(None, description="Filter by minimum amount"),
    max_amount: Optional[int] = Query(None, description="Filter by maximum amount"),
    limit: Optional[int] = Query(50, description="Number of records to return"),
    offset: Optional[int] = Query(0, description="Number of records to skip")
):
    """Get donation history for the current user with optional filters"""
    try:
        # Base query for current user's donations
        query = select(Donation).where(Donation.user_id == current_user.id)
        
        # Apply filters
        filters = []
        
        if payment_status:
            filters.append(Donation.payment_status.ilike(f"%{payment_status}%"))
        
        if payment_method:
            filters.append(Donation.payment_method.ilike(f"%{payment_method}%"))
        
        if start_date:
            filters.append(Donation.payment_date >= start_date)
        
        if end_date:
            filters.append(Donation.payment_date <= end_date)
        
        if min_amount is not None:
            filters.append(Donation.amount >= min_amount)
        
        if max_amount is not None:
            filters.append(Donation.amount <= max_amount)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply ordering, limit, and offset
        query = query.order_by(Donation.payment_date.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        donations = result.scalars().all()
         
        print(f"Found {len(donations)} donation records for user {current_user.id}")
        return donations
    
    except Exception as e:
        print(f"Error getting donation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get donation history: {str(e)}")

def convert_amount_to_words(amount):
    """Convert amount to words (simplified version)"""
    try:
        if amount == 0:
            return "Zero Only"
        
        # For simplicity, handling up to thousands
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        if amount < 10:
            return f"{units[amount]} Only"
        elif amount < 20:
            return f"{teens[amount - 10]} Only"
        elif amount < 100:
            return f"{tens[amount // 10]} {units[amount % 10] if amount % 10 != 0 else ''} Only".strip()
        elif amount < 1000:
            hundreds = amount // 100
            remainder = amount % 100
            result = f"{units[hundreds]} Hundred"
            if remainder > 0:
                result += f" {convert_amount_to_words(remainder).replace(' Only', '')}"
            return f"{result} Only"
        else:
            # For amounts >= 1000, return a simplified version
            return f"INR {amount} Only"
    except:
        return f"INR {amount} Only"

@router.get("/donation_bill/{donation_id}", response_model=DonationBillOut)
async def get_donation_bill(
    donation_id: int,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user: UserProfile = Depends(get_current_user_object)
):
    """Generate donation bill/receipt for a specific donation"""
    try:
        # Get donation with user and ngo_post details
        query = select(Donation).options(
            selectinload(Donation.user),
            selectinload(Donation.ngo_post)
        ).where(
            and_(
                Donation.id == donation_id,
                Donation.user_id == current_user.id
            )
        )
        
        result = await db.execute(query)
        donation = result.scalars().first()
        
        if not donation:
            raise HTTPException(status_code=404, detail="Donation not found or not authorized")
        
        # Generate receipt number using order_id and date
        receipt_no = f"NGO/{donation.payment_date.year}/{donation.order_id:04d}"
        
        # Format date
        formatted_date = donation.payment_date.strftime("%d-%b-%Y")
        
        # Get donor details
        donor_name = f"{donation.user.first_name} {donation.user.last_name}"
        donor_email = donation.user.email
        donor_pan = donation.user.pan_card if donation.user.pan_card else None
        
        # Get NGO details (use ngo_post header as NGO name, fallback to static)
        ngo_name = donation.ngo_post.header if donation.ngo_post else "Jeevan Prakash Foundation"
        purpose_of_donation = donation.ngo_post.description if donation.ngo_post else "Medical Aid for Child in Need"
        
        # Convert amount to words
        amount_in_words = convert_amount_to_words(donation.amount)
        
        # Create bill response
        bill_data = DonationBillOut(
            receipt_no=receipt_no,
            date=formatted_date,
            ngo_name=ngo_name,
            donor_name=donor_name,
            donor_email=donor_email,
            donor_pan=donor_pan,
            amount_donated=donation.amount,
            mode_of_payment=donation.payment_method.upper(),
            reference_no=donation.transaction_id,
            purpose_of_donation=purpose_of_donation,
            amount_in_words=amount_in_words
        )
        
        print(f"Generated bill for donation {donation_id} for user {current_user.id}")
        return bill_data
        
    except Exception as e:
        print(f"Error generating donation bill: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate donation bill: {str(e)}")