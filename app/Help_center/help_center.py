from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import time
from sqlalchemy.orm import selectinload
from app.database import SessionLocal
from app.models import IssueType, IssueOption, ChatSupport, FAQ
from app.schemas import IssueTypeOut, IssueOptionOut
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models import SupportTicket
from app.schemas import SupportTicketCreate, SupportTicketOut, ChatSupportCreate, ChatSupportOut
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..models import FAQ
from ..schemas import FAQOut, FAQSearch



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
    except JWTError:
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
    db: AsyncSession = Depends(get_db),
    _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)
):
    result = await db.execute(select(SupportTicket))
    tickets = result.scalars().all()
    return tickets

@router.get("/ticket_history", response_model=List[SupportTicketOut])
async def ticket_history(user_id: int,  db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key),
    _user=Depends(get_current_user)):
    try:
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.user_id == user_id)
        )
        tickets = result.scalars().all()
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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
