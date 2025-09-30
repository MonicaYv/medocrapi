
# === main.py ===
from app.help_center import help_center
from app.profile import user_profile
from app.payments import user_payments
from app.Help_center import help_center

app.include_router(help_center.router)
app.include_router(user_profile.router)
app.include_router(user_payments.router)
app.include_router(help_center.router)

# ====  models.py ====
from sqlalchemy.orm import relationship
from datetime import datetime


class IssueType(Base):
    __tablename__ = "support_issuetype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # One-to-many relationship
    options = relationship("IssueOption", back_populates="issue_type")


class IssueOption(Base):
    __tablename__ = "support_issueoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    issue_type_id = Column(Integer, ForeignKey("support_issuetype.id"), nullable=False)

    # Many-to-one to IssueType
    issue_type = relationship("IssueType", back_populates="options")

    # One-to-many to SupportTicket
    tickets = relationship("SupportTicket", back_populates="issue_option")  


class SupportTicket(Base):
    __tablename__ = "support_supportticket"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image = Column(String, nullable=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_id = Column(Integer, nullable=True)
    issue_option_id = Column(Integer, ForeignKey("support_issueoption.id"))
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    assigned_to = Column(Integer, nullable=True)

    # Correct relationship to IssueOption
    issue_option = relationship("IssueOption", back_populates="tickets")


class ChatSupport(Base):
    __tablename__ = "support_chat"  # FIXED here ✅

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    message = Column(Text, nullable=False)
    sender_type = Column(String, nullable=False)  # 'user' or 'agent'
    sender_id = Column(Integer, nullable=True)
    session_status = Column(String, default="active")  # active, closed, waiting
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    message_type = Column(String, default="text")  # text, image, file
    attachment_url = Column(String, nullable=True)

class FAQ(Base):
    __tablename__ = "account_faq"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    profile_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("UserProfile.id"))  
    # user = relationship("UserProfile", back_populates="faqs")  



class IssueType(Base):
    __tablename__ = "support_issuetype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # One-to-many relationship
    options = relationship("IssueOption", back_populates="issue_type")


class IssueOption(Base):
    __tablename__ = "support_issueoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    issue_type_id = Column(Integer, ForeignKey("support_issuetype.id"), nullable=False)

    # Many-to-one to IssueType
    issue_type = relationship("IssueType", back_populates="options")

    # One-to-many to SupportTicket
    tickets = relationship("SupportTicket", back_populates="issue_option")  


class SupportTicket(Base):
    __tablename__ = "support_supportticket"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image = Column(String, nullable=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_id = Column(Integer, nullable=True)
    issue_option_id = Column(Integer, ForeignKey("support_issueoption.id"))
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    assigned_to = Column(Integer, nullable=True)

    # Correct relationship to IssueOption
    issue_option = relationship("IssueOption", back_populates="tickets")

class ChatSupport(Base):
    __tablename__ = "chat_support"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    message = Column(String, nullable=False)
    sender_type = Column(String, nullable=False)  # 'user' or 'agent'
    sender_id = Column(Integer, nullable=True)
    session_status = Column(String, default="active")  # active, closed, waiting
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    message_type = Column(String, default="text")  # text, image, file
    attachment_url = Column(String, nullable=True)
    
    # Relationships
    user = relationship("UserProfile")


class EmailSupport(Base):
    __tablename__ = "support_email"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    email = Column(String, nullable=False)  # User's email
    status = Column(String, default="pending")  # pending, replied, closed
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserProfile")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    card_holder_name = Column(String, nullable=False)
    card_number_masked = Column(String, nullable=False)  # e.g., "**** **** **** 1234"
    card_type = Column(String, nullable=False)  # visa, mastercard, amex, etc.
    expiry_month = Column(Integer, nullable=False)  # 1-12
    expiry_year = Column(Integer, nullable=False)  # 2025, 2026, etc.
    is_default = Column(Boolean, default=False)
    payment_gateway = Column(String, default="stripe")  # stripe, razorpay, etc.
    status = Column(String, default="active")  # active, expired, deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserProfile")

class PointsBadge(Base):
    __tablename__ = "points_pointsbadge"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    min_points = Column(Integer, nullable=False)
    max_points = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)  # URL to the badge image


# === schemas.py ===
from datetime import datetime, date
from typing import Optional, List


#help center

class IssueTypeBase(BaseModel):
    name: str

class IssueTypeOut(IssueTypeBase):
    id: int

    class Config:
        from_attributes = True

# --- For GET /api/issue_option?issue_type_id=1 ---
class IssueOptionBase(BaseModel):
    name: str
    issue_type_id: int

class IssueOptionOut(IssueOptionBase):
    id: int

    class Config:
        from_attributes = True

class SupportTicketBase(BaseModel):
    description: str
    image: Optional[str] = None
    status: Optional[str] = "open"
    created_by_id: int
    issue_option_id: int
    user_id: int
    assigned_to: Optional[int] = None

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketOut(SupportTicketBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Email Support Schemas
class EmailSupportCreate(BaseModel):
    subject: str
    message: str
    priority: Optional[str] = "normal"

class EmailSupportOut(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    email: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmailSupportUpdateStatus(BaseModel):
    status: str  # pending, replied, closed


# Payment Methods Schemas
class PaymentMethodCreate(BaseModel):
    card_holder_name: str
    card_number_masked: str  # e.g., "**** **** **** 1234"
    card_type: str  # visa, mastercard, amex, etc.
    expiry_month: int  # 1-12
    expiry_year: int  # 2025, 2026, etc.
    is_default: Optional[bool] = False
    payment_gateway: Optional[str] = "stripe"

class PaymentMethodUpdate(BaseModel):
    card_holder_name: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: Optional[bool] = None

class PaymentMethodOut(BaseModel):
    id: int
    user_id: int
    card_holder_name: str
    card_number_masked: str
    card_type: str
    expiry_month: int
    expiry_year: int
    is_default: bool
    payment_gateway: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Points and Badges Schemas

class PointsBadgeCreate(BaseModel):
    name: str



# === help_center.py ===
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import time
import asyncio
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import IssueType, IssueOption, UserProfile, EmailSupport
from app.schemas import IssueTypeOut, IssueOptionOut, EmailSupportCreate, EmailSupportOut, EmailSupportUpdateStatus
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM
from app.models import SupportTicket
from app.schemas import SupportTicketCreate, SupportTicketOut
from app.profile.user_auth import get_current_user_object
from app.email_utils import send_email

router = APIRouter(
    prefix="/help",
    tags=["Help Center"]
)


def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# ✅ GET /api/issue_type - Only id & name
@router.get("/api/issue_type", response_model=List[IssueTypeOut])
async def get_issue_types(db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    result = await db.execute(select(IssueType))
    issue_types = result.scalars().all()
    return issue_types

# ✅ GET /api/issue_option?issue_type_id=1 - Only options for a given issue_type
@router.get("/api/issue_option", response_model=List[IssueOptionOut])
async def get_issue_options(issue_type_id: int = Query(...), db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    result = await db.execute(
        select(IssueOption).where(IssueOption.issue_type_id == issue_type_id)
    )
    options = result.scalars().all()
    if not options:
        raise HTTPException(status_code=404, detail="No options found for given IssueType ID")
    return options

#  Get/api/supportTicket

@router.post("/create_support_ticket", response_model=SupportTicketOut)
async def create_support_ticket(ticket: SupportTicketCreate, db: AsyncSession = Depends(get_db)):
    new_ticket = SupportTicket(**ticket.dict())
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return new_ticket

@router.get("/get_all_support_tickets", response_model=list[SupportTicketOut])
async def get_all_support_tickets(
    search_text: str = Query(None, description="Search in ticket description"),
    status: str = Query(None, description="Filter by ticket status (open, closed, in_progress)"),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get all support tickets with optional search and filters"""
    
    # Base query for all support tickets
    query = select(SupportTicket)
    
    # Apply search filter if provided
    if search_text:
        query = query.where(SupportTicket.description.ilike(f"%{search_text}%"))
    
    # Apply status filter if provided
    if status:
        query = query.where(SupportTicket.status == status)
    
    # Order by most recent first
    query = query.order_by(SupportTicket.created_at.desc())
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


# ========== EMAIL SUPPORT APIs ==========

@router.post("/create_email_support", response_model=EmailSupportOut)
async def create_email_support(
    email_data: EmailSupportCreate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):  
    try:
        # Create new email support record
        new_email_support = EmailSupport(
            user_id=current_user.id,
            subject=email_data.subject,
            message=email_data.message,
            email=current_user.email,
            priority=email_data.priority,
            status="pending"
        )
        
        db.add(new_email_support)
        await db.commit()
        await db.refresh(new_email_support)
        
        # Send confirmation email to user
        confirmation_message = f"""
        Dear {current_user.first_name},
        
        Your email support request has been received successfully.
        
        Support Ticket ID: ES-{new_email_support.id}
        Subject: {email_data.subject}
        Priority: {email_data.priority}
        
        Our support team will get back to you within 24-48 hours.
        
        Thank you for contacting us!
        
        Best regards,
        MedoCRM Support Team
        """

        try:
            asyncio.create_task(
                send_email(
                    current_user.email,
                    f"Support Request Received - ES-{new_email_support.id}",
                    confirmation_message
                )
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send email: {e}")
        
        return new_email_support
        
    except Exception as e:
        await db.rollback()
        print(f"Error creating email support: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create email support: {str(e)}")


@router.get("/get_user_email_support", response_model=list[EmailSupportOut])
async def get_user_email_support(
    search_text: str = Query(None, description="Search in subject and message"),
    status: str = Query(None, description="Filter by status (pending, replied, closed)"),
    priority: str = Query(None, description="Filter by priority (low, normal, high, urgent)"),
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Get current user's email support history with optional search and filters"""
    
    # Base query for current user's email support
    query = select(EmailSupport).where(EmailSupport.user_id == current_user.id)
    
    # Apply search filter if provided
    if search_text:
        search_condition = (
            EmailSupport.subject.ilike(f"%{search_text}%") |
            EmailSupport.message.ilike(f"%{search_text}%")
        )
        query = query.where(search_condition)
    
    # Apply status filter if provided
    if status:
        query = query.where(EmailSupport.status == status)
        
    # Apply priority filter if provided
    if priority:
        query = query.where(EmailSupport.priority == priority)
    
    # Order by most recent first
    query = query.order_by(EmailSupport.created_at.desc())
    
    result = await db.execute(query)
    email_supports = result.scalars().all()
    return email_supports


@router.put("/update_email_support_status/{support_id}", response_model=EmailSupportOut)
async def update_email_support_status(
    support_id: int,
    status_data: EmailSupportUpdateStatus,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    """Update email support status (Admin only endpoint)"""
    query = select(EmailSupport).where(EmailSupport.id == support_id)
    result = await db.execute(query)
    email_support = result.scalars().first()
    
    if not email_support:
        raise HTTPException(status_code=404, detail="Email support request not found")
    
    # Update status
    email_support.status = status_data.status
    await db.commit()
    await db.refresh(email_support)
    
    # Get user details for notification
    user_query = select(UserProfile).where(UserProfile.id == email_support.user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    
    if user:
        # Send status update email to user
        status_message = f"""
        Dear {user.first_name},
        
        Your email support request has been updated.
        
        Support Ticket ID: ES-{email_support.id}
        Subject: {email_support.subject}
        Status: {status_data.status.upper()}
        
        {
            "Thank you for your patience. Our team is working on your request." if status_data.status == "replied" 
            else "Your support request has been resolved. Thank you for contacting us!" if status_data.status == "closed"
            else "Your request is being processed."
        }
        
        Best regards,
        MedoCRM Support Team
        """
        
        # Send notification email
        try:
            asyncio.create_task(
                send_email(
                    user.email,
                    f"Support Update - ES-{email_support.id}",
                    status_message
                )
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send notification email: {e}")
    
    return email_support



