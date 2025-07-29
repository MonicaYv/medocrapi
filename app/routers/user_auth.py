from fastapi import APIRouter, Header, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
import asyncio
from jose import jwt
from datetime import datetime, timedelta
import os, re
from app.models import UserProfile
from app.schemas import ContactInfo, RegisterFinal, VerifyLoginOTP, UserProfileOut, Token
from app.otp_utils import generate_otp_secret, generate_otp, verify_otp
from app.email_utils import send_email
from app.database import get_db 
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def is_email(contact: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', contact))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def check_authorization_key(authorization_key: str = Header(...)):
    if authorization_key != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Invalid authorization key")
    return authorization_key

@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_registration_otp(data: ContactInfo, db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    if is_email(data.contact):
        query = select(UserProfile).where(UserProfile.email == data.contact)
    else:
        query = select(UserProfile).where(UserProfile.phone_number == data.contact)

    existing_user = await db.execute(query)
    if existing_user.scalars().first():
        raise HTTPException(status_code=409, detail="An account with this contact info already exists.")

    otp_secret = generate_otp_secret()
    otp = generate_otp(otp_secret)

    if is_email(data.contact):
        asyncio.create_task(send_email(data.contact, "Your Registration Code", f"Your code is: {otp}"))
    else:
        #sms function would be called here
        print(f"SMS to {data.contact}: Your code is {otp}")
    return {"otp_token": otp_secret, "message": "OTP sent."}

@router.post("/register", response_model=UserProfileOut)
async def register_user(data: RegisterFinal, db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    if not verify_otp(data.otp_token, data.otp):
        raise HTTPException(status_code=401, detail="Invalid or expired OTP.")

    new_user = UserProfile(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone_number=data.phone_number,
        otp_secret=data.otp_token,
        is_active=True,
        gender=data.gender,
        age=data.age
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login/request-otp", status_code=status.HTTP_200_OK)
async def request_login_otp(data: ContactInfo, db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    if is_email(data.contact):
        query = select(UserProfile).where(UserProfile.email == data.contact)
    else:
        query = select(UserProfile).where(UserProfile.phone_number == data.contact)

    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not user.otp_secret:
        raise HTTPException(status_code=404, detail="User not found or not set up for OTP login.")

    otp = generate_otp(user.otp_secret)
    if is_email(user.email):
        asyncio.create_task(send_email(user.email, "Your Login Code", f"Your code is: {otp}"))
    else:
        #sms function would be called here
        print(f"SMS to {user.phone_number}: Your code is {otp}")
    return {"message": "OTP sent."}


@router.post("/login/verify", response_model=Token)
async def verify_login_and_get_token(data: VerifyLoginOTP, db: AsyncSession = Depends(get_db), _auth=Depends(check_authorization_key)):
    if is_email(data.contact):
        query = select(UserProfile).where(UserProfile.email == data.contact)
    else:
        query = select(UserProfile).where(UserProfile.phone_number == data.contact)

    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not user.otp_secret or not verify_otp(user.otp_secret, data.otp):
        raise HTTPException(status_code=401, detail="Invalid contact or OTP.")

    # Create a JWT token for the authenticated user
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}