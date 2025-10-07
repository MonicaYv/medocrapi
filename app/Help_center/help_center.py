import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.database import get_db
from app.models import (
    IssueType, IssueOption, SupportTicket,
    ChatSupport, EmailSupport
)
from app.schemas import (
    IssueTypeOut, SupportTicketOut, IssueOptionOut,
    ChatSupportOut, ChatSupportCreate,
    EmailSupportOut, EmailSupportUpdateStatus, EmailSupportCreate,
    FAQOut, 
)
from app.profile.user_auth import (
    get_current_user_object, check_authorization_key, get_current_user
)
from app.email_utils import send_email
from uuid import uuid4
from pathlib import Path
import shutil
import json

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(
    prefix="/help",
    tags=["Help Center"]
)

@router.get("/issue_type", response_model=List[IssueTypeOut])
async def get_issue_types(
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    result = await db.execute(select(IssueType))
    return result.scalars().all()

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

@router.post("/create_support_ticket", response_model=SupportTicketOut)
async def create_support_ticket(
    ticket: str = Form(...),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    current_user=Depends(get_current_user_object)
):
    # Parse the JSON string into a dict
    try:
        ticket_data = json.loads(ticket)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for ticket")
    user, profile = current_user
    ticket_data["user_id"] = user.id

    # Save file to disk and store path only
    if image:
        file_ext = Path(image.filename).suffix
        filename = f"{uuid4().hex}{file_ext}"
        file_path = UPLOAD_DIR / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)  # safely copy bytes to file
        ticket_data["image"] = str(file_path)  # only path is stored

    if ticket_data.get("assigned_to") is not None:
        ticket_data["assigned_to"] = str(ticket_data["assigned_to"])

    # Default created_by_id
    if not ticket_data.get("created_by_id"):
        ticket_data["created_by_id"] = user.id

    # Create the ticket object
    new_ticket = SupportTicket(**ticket_data)
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)

    return new_ticket

@router.get("/ticket-history", response_model=List[SupportTicketOut])
async def get_all_support_tickets(
    search_text: Optional[str] = Query(None, description="Search in ticket description"),
    status: Optional[str] = Query(None, description="Filter by ticket status"),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    query = select(SupportTicket)
    if search_text:
        query = query.where(SupportTicket.description.ilike(f"%{search_text}%"))
    if status:
        query = query.where(SupportTicket.status == status)
    query = query.order_by(SupportTicket.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/chat_history", response_model=List[ChatSupportOut])
async def chat_history(
    chat_session_id: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    query = select(ChatSupport)
    if chat_session_id:
        query = query.where(ChatSupport.chat_session_id == chat_session_id)
    elif user_id:
        query = query.where(ChatSupport.user_id == user_id)

    query = query.order_by(ChatSupport.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()

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

@router.post("/create_email_support", response_model=EmailSupportOut)
async def create_email_support(
    email_data: EmailSupportCreate,
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, profile = current_user
    try:
        new_email_support = EmailSupport(
            user_id=user.id,
            subject=email_data.subject,
            message=email_data.message,
            email=user.email,
            priority=email_data.priority,
            status="pending"
        )
        db.add(new_email_support)
        await db.commit()
        await db.refresh(new_email_support)

        confirmation_message = f"""
        Dear {profile.first_name},

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
                    user.email,
                    f"Support Request Received - ES-{new_email_support.id}",
                    confirmation_message
                )
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

        return new_email_support

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create email support: {str(e)}")

@router.get("/get_user_email_support", response_model=List[EmailSupportOut])
async def get_user_email_support(
    search_text: Optional[str] = Query(None, description="Search in subject and message"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    current_user=Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    user, _ = current_user
    query = select(EmailSupport).where(EmailSupport.user_id == user.id)
    if search_text:
        query = query.where(
            EmailSupport.subject.ilike(f"%{search_text}%") |
            EmailSupport.message.ilike(f"%{search_text}%")
        )
    if status:
        query = query.where(EmailSupport.status == status)
    if priority:
        query = query.where(EmailSupport.priority == priority)

    query = query.order_by(EmailSupport.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/update_email_support_status/{support_id}", response_model=EmailSupportOut)
async def update_email_support_status(
    support_id: int,
    status_data: EmailSupportUpdateStatus,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key)
):
    result = await db.execute(select(EmailSupport).where(EmailSupport.id == support_id))
    email_support = result.scalars().first()
    if not email_support:
        raise HTTPException(status_code=404, detail="Email support request not found")

    email_support.status = status_data.status
    await db.commit()
    await db.refresh(email_support)
    return email_support