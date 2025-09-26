from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import time
import asyncio
from app.database import get_db, SessionLocal
from app.models import IssueType, IssueOption, ChatSupport, FAQ, EmailSupport, UserProfile, SupportTicket
from app.schemas import (
    IssueTypeOut, IssueOptionOut, SupportTicketCreate, SupportTicketOut, 
    ChatSupportCreate, ChatSupportOut, EmailSupportCreate, EmailSupportOut, 
    EmailSupportUpdateStatus, FAQOut
)
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.routers.user_auth import get_current_user_object
from app.email_utils import send_email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# JWT token validation dependency
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return email

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# ✅ GET /api/issue_type - Only id & name
@router.get("/issue_type", response_model=List[IssueTypeOut])
async def get_issue_types(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    result = await db.execute(select(IssueType))
    issue_types = result.scalars().all()
    return issue_types

# ✅ GET /api/issue_option?issue_type_id=1 - Only options for a given issue_type
@router.get("/issue_option", response_model=List[IssueOptionOut])
async def get_issue_options(
    issue_type_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    result = await db.execute(
        select(IssueOption).where(IssueOption.issue_type_id == issue_type_id)
    )
    options = result.scalars().all()
    if not options:
        raise HTTPException(status_code=404, detail="No options found for given IssueType ID")
    return options

#  Get/api/supportTicket

@router.post("/create_support_ticket", response_model=SupportTicketOut)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
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
    

@router.get("/chat_history", response_model=List[ChatSupportOut])
async def chat_history(
    chat_session_id: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    try:
        query = select(ChatSupport)

        if chat_session_id:
            query = query.where(ChatSupport.chat_session_id == chat_session_id)
        elif user_id:
            query = query.where(ChatSupport.user_id == user_id)

        query = query.order_by(ChatSupport.created_at.asc())
        result = await db.execute(query)
        chats = result.scalars().all()

        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send_message", response_model=ChatSupportOut)
async def send_message(
    chat: ChatSupportCreate,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    new_chat = ChatSupport(**chat.dict())
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat

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



@router.get("/faq_list", response_model=List[FAQOut])
async def get_faqs(
    keyword: Optional[str] = Query(None, description="Search keyword in question or answer"),
    category: Optional[str] = Query(None, description="Filter by category"),
    profile_type: str = Query("user", description="Filter by profile type (default: user)"),
    db: AsyncSession = Depends(get_db)
):
    query = select(FAQ)

    # Apply profile type filter (default is 'user')
    if profile_type:
        query = query.filter(FAQ.profile_type == profile_type)

    # Apply keyword filter if provided
    if keyword:
        keyword = f"%{keyword.lower()}%"
        query = query.filter(
            (FAQ.question.ilike(keyword)) | (FAQ.answer.ilike(keyword))
        )

    # Apply category filter if provided
    if category:
        query = query.filter(FAQ.category == category)

    result = await db.execute(query)
    return result.scalars().all()
