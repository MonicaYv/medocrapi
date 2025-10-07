from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, join
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from decimal import Decimal
import uuid
from app.file_utils import validate_and_save_file
from app.models import Donation, NGOPost, NGOProfile, ContactPerson, PointsActionType, RewardHistory, User, PostType
from app.schemas import DonationOut, PostTypeOut, DonationBillOut, NGOPostResponse
from app.profile.user_auth import get_current_user_object, check_authorization_key
from app.config import COMPANY, GSTIN, ADDRESS, CONTACT, EMAIL

router = APIRouter( 
    prefix="/donation",
    tags=["donation"]
)

def convert_amount_to_words(amount: float) -> str:
    """Convert numeric amount into words (Indian numbering system)."""
    try:
        if amount == 0:
            return "Zero Only"

        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
                 "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        scales = ["", "Thousand", "Lakh", "Crore"]

        def two_digit_word(n):
            if n < 10:
                return units[n]
            elif n < 20:
                return teens[n - 10]
            else:
                return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")

        def three_digit_word(n):
            word = ""
            if n > 99:
                word += units[n // 100] + " Hundred"
                if n % 100 != 0:
                    word += " " + two_digit_word(n % 100)
            else:
                word += two_digit_word(n)
            return word

        num = int(amount)
        decimal_part = round((amount - num) * 100)

        words = []
        i = 0
        while num > 0:
            if i == 0:
                words.append(three_digit_word(num % 1000))
                num //= 1000
            else:
                words.append(two_digit_word(num % 100) + " " + scales[i])
                num //= 100
            i += 1

        words = [w for w in reversed(words) if w.strip() != ""]
        amount_words = " ".join(words)

        if decimal_part > 0:
            amount_words += f" and {decimal_part}/100"

        return f"INR {amount_words} Only"
    except:
        return f"INR {amount} Only"
  
 # =========== Donation APIs ===========
@router.get("/posts", response_model=list[NGOPostResponse])
async def get_active_donation_posts(
    ngo_name: Optional[str] = Query(None, description="Filter by NGO name"),
    post_type_name: Optional[str] = Query(None, description="Filter by Post Type name"),
    db: AsyncSession = Depends(get_db)
):
    # Start with NGOPost
    query = select(NGOPost, NGOProfile, PostType).join(
        User, NGOPost.user_id == User.id
    ).join(
        NGOProfile, NGOProfile.user_id == User.id
    ).join(
        PostType, NGOPost.post_type_id == PostType.id
    )

    # Filters
    if ngo_name:
        query = query.where(NGOProfile.ngo_name.ilike(f"%{ngo_name}%"))
    if post_type_name:
        query = query.where(PostType.name.ilike(f"%{post_type_name}%"))
    
    query = query.where(
        NGOPost.status == "Ongoing",
        NGOPost.end_date >= date.today()
    )

    result = await db.execute(query)
    rows = result.all()  # Each row = (NGOPost, NGOProfile, PostType)

    response = []
    for post_row, ngo, post_type in rows:
        response.append(NGOPostResponse(
            id=post_row.id,
            user_id=post_row.user_id,
            header=post_row.header,
            description=post_row.description,
            tags=post_row.tags,
            post_type=post_type.name,  # <-- return name instead of id
            donation_frequency=post_row.donation_frequency,
            target_donation=post_row.target_donation,
            donation_received=post_row.donation_received,
            # Country/State/City lookups if needed
            country=(await db.get(NGOPost.country.property.mapper.class_, post_row.country_id)).name
                    if post_row.country_id else None,
            state=(await db.get(NGOPost.state.property.mapper.class_, post_row.state_id)).name
                    if post_row.state_id else None,
            city=(await db.get(NGOPost.city.property.mapper.class_, post_row.city_id)).name
                    if post_row.city_id else None,
            pincode=post_row.pincode,
            age_group=(await db.get(NGOPost.age_group.property.mapper.class_, post_row.age_group_id)).name
                      if post_row.age_group_id else None,
            gender=(await db.get(NGOPost.gender.property.mapper.class_, post_row.gender_id)).name
                      if post_row.gender_id else None,
            spending_power=(await db.get(NGOPost.spending_power.property.mapper.class_, post_row.spending_power_id)).name
                             if post_row.spending_power_id else None,
            start_date=post_row.start_date,
            end_date=post_row.end_date,
            status=post_row.status,
            creative1=post_row.creative1,
            creative2=post_row.creative2,
            views=post_row.views,
            saved=post_row.saved,
            last_downloaded=post_row.last_downloaded,
            created_at=post_row.created_at,
            updated_at=post_row.updated_at,
            ngo_name=ngo.ngo_name,  
            ngo_city=ngo.city,
            ngo_state=ngo.state,
            ngo_country=ngo.country,
            ngo_pincode=ngo.pincode,
            ngo_address=ngo.address,
        ))

    return response


@router.get("/post_types", response_model=List[PostTypeOut])
async def get_post_types(
    db: AsyncSession = Depends(get_db), 
    _auth=Depends(check_authorization_key),
    current_user = Depends(get_current_user_object)
):
    try:
        query = select(PostType).where(PostType.is_active == True)
        result = await db.execute(query)
        post_types = result.scalars().all()
        return post_types
    except Exception as e:
        print(f"Error getting post types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get post types: {str(e)}")

@router.post("/pay/{post_id}")
async def donate_pay(
    post_id: int,
    donation_amount: float = Form(...),
    pan_number: str = Form(...),
    pan_document: UploadFile = Form(...),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    user, _ = current_user

    # Fetch post
    post_query = select(NGOPost).where(NGOPost.id == post_id)
    post_result = await db.execute(post_query)
    post = post_result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Minimum amount check
    if donation_amount < 100:
        raise HTTPException(status_code=400, detail="Minimum donation is ₹100")

    # Target limit check
    donation_received = Decimal(post.donation_received or 0)
    if donation_received + Decimal(str(donation_amount)) > post.target_donation:
        raise HTTPException(status_code=400, detail="Donation exceeds target amount")

    # Frequency check
    freq = (post.donation_frequency or "once").lower()
    user_donations_query = select(Donation).where(and_(Donation.ngopost_id == post.id, Donation.user_id == user.id))
    user_donations = (await db.execute(user_donations_query)).scalars().all()

    allowed = 1 if "one" in freq else 2 if "two" in freq else 3 if "three" in freq else 1
    if len(user_donations) >= allowed:
        raise HTTPException(status_code=400, detail=f"You can donate only {allowed} time(s) to this post.")

    # PAN validation
    if not pan_number or len(pan_number) != 10:
        raise HTTPException(status_code=400, detail="Invalid PAN number")

    # Save PAN document
    pan_document_path, error = validate_and_save_file(
        pan_document, "donation_docs", "PAN Document", user_type="common"
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Calculate charges
    platform_fee = round(donation_amount * 0.02, 2)
    gst = round(platform_fee * 0.18, 2)
    amount_to_ngo = round(donation_amount - platform_fee - gst, 2)

    # Generate IDs
    order_id = uuid.uuid4().hex[:8]
    transaction_id = uuid.uuid4().hex[:8]

    # Create donation record
    donation = Donation(
        ngopost_id=post.id,
        user_id=user.id,
        amount=donation_amount,
        payment_method="UPI",
        pan_number=pan_number,
        pan_document=pan_document_path,
        payment_status="Success",
        order_id=order_id,
        payment_date=datetime.utcnow(),
        gst=gst,
        platform_fee=platform_fee,
        amount_to_ngo=amount_to_ngo,
        transaction_id=transaction_id,
    )
    db.add(donation)

    # Update post donation total
    post.donation_received = float(donation_received + Decimal(str(donation_amount)))
    db.add(post)

    # Add reward points (if available)
    try:
        action_type_query = select(PointsActionType).where(PointsActionType.action_type == "Donate")
        action_type = (await db.execute(action_type_query)).scalars().first()
        if action_type:
            points_entry = RewardHistory(
                user_id=user.id,
                action_type_id=action_type.id,
                points=action_type.default_points,
                timestamp=datetime.utcnow()
            )
            db.add(points_entry)
    except Exception as e:
        print("PointsActionType missing:", e)

    # Commit all
    await db.commit()

    return {
        "success": True,
        "order_id": order_id,
        "transaction_id": transaction_id
    }

@router.get("/donation_history", response_model=List[DonationOut])
async def get_donation_history(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user = Depends(get_current_user_object),
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
    user, profile = current_user
    try:
        query = select(Donation).where(Donation.user_id == user.id)
        
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
        query = query.order_by(Donation.payment_date.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        donations = result.scalars().all()
        print(f"Found {len(donations)} donation records for user {user.id}")
        return donations
    
    except Exception as e:
        print(f"Error getting donation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get donation history: {str(e)}")
    
@router.get("/donation_bill/{donation_id}", response_model=DonationBillOut)
async def get_donation_bill(
    donation_id: int,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user
    query = (
        select(Donation)
        .options(selectinload(Donation.ngopost).selectinload(NGOPost.user))
        .where(and_(Donation.id == donation_id, Donation.user_id == user.id))
    )
    result = await db.execute(query)
    donation = result.scalars().first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    ngo_user = donation.ngopost.user
    ngo_profile_query = select(NGOProfile).where(NGOProfile.user_id == ngo_user.id)
    ngo_profile = (await db.execute(ngo_profile_query)).scalars().first()

    contact_query = select(ContactPerson).where(ContactPerson.profile_id_id == user.id)
    contact_person = (await db.execute(contact_query)).scalars().first()
    amount_in_words=convert_amount_to_words(donation.amount)
    platform_details = {
        "company": COMPANY,
        "gstin": GSTIN,
        "address": ADDRESS,
        "email": EMAIL,
        "phone": CONTACT
        }
    return DonationBillOut(
        receipt_no=f"NGO-{donation.id}",
        date=donation.payment_date.strftime("%d-%b-%Y"),
        ngo_name=ngo_profile.ngo_name if ngo_profile else "N/A",
        donor_name=contact_person.name if contact_person else f"{profile.first_name} {profile.last_name}",
        donor_email=user.email,
        amount_donated=donation.amount,
        mode_of_payment=donation.payment_method,
        reference_no=donation.transaction_id,
        purpose_of_donation=donation.ngopost.header if donation.ngopost else "Donation",
        amount_in_words=amount_in_words,
        platform_details=platform_details
    )

@router.get("/platform_bill/{donation_id}", response_model=DonationBillOut)
async def get_platform_bill(
    donation_id: int,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    query = (
        select(Donation)
        .options(selectinload(Donation.ngopost).selectinload(NGOPost.user))
        .where(and_(Donation.id == donation_id, Donation.user_id == user.id))
    )
    result = await db.execute(query)
    donation = result.scalars().first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    total = float(donation.amount or 0) + float(donation.gst or 0)
    amount_in_words = convert_amount_to_words(total)
    platform_details = {
        "company": COMPANY,
        "gstin": GSTIN,
        "address": ADDRESS,
        "email": EMAIL,
        "phone": CONTACT
        }
    return DonationBillOut(
        receipt_no=f"PLATFORM-{donation.id}", 
        date=donation.payment_date.strftime("%d-%b-%Y"),
        ngo_name=donation.ngopost.header if donation.ngopost else "Platform",
        donor_name=f"{profile.first_name} {profile.last_name}" if profile else "N/A",
        donor_email=user.email,
        amount_donated=float(donation.amount),
        mode_of_payment=donation.payment_method,
        reference_no=donation.transaction_id or "",
        purpose_of_donation=donation.ngopost.header if donation.ngopost else "Donation",
        amount_in_words=amount_in_words,
        platform_details=platform_details
    )


@router.post("/toggle_saved")
async def toggle_saved_donation(
    donation_id: int = Form(...),
    action: str = Form(...),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    user, _ = current_user

    if action not in ["save", "unsave"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Load donation
    query = select(Donation).where(and_(Donation.id == donation_id, Donation.user_id == user.id))
    result = await db.execute(query)
    donation: Donation = result.scalars().first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    # Update the saved status
    donation.saved = (action == "save")
    db.add(donation)
    await db.commit()

    await db.refresh(donation)

    return {
        "success": True,
        "saved": donation.saved,
        "donation_id": donation.id,
    }

@router.get("/export")
async def export_donation_history(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    user, _ = current_user
    query = select(Donation).where(Donation.user_id == user.id).order_by(Donation.created_at.desc())
    result = await db.execute(query)
    donations = result.scalars().all()

    return {
        "total_items": len(donations),
        "donations": [
            {
                "id": d.id,
                "amount": float(d.amount),
                "status": d.payment_status,
                "method": d.payment_method,
                "created_at": d.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for d in donations
        ]
    }