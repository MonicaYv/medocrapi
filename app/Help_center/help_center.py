from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import time
from sqlalchemy.orm import selectinload
from app.database import SessionLocal
from app.models import IssueType, IssueOption
from app.schemas import IssueTypeOut, IssueOptionOut
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models import SupportTicket
from app.schemas import SupportTicketCreate, SupportTicketOut



router = APIRouter()

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

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
async def get_all_support_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SupportTicket))
    tickets = result.scalars().all()
    return tickets