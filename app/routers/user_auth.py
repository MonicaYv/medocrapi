from fastapi import APIRouter, Header, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio
import jwt
import re
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
import random, string
from app.models import UserProfile, UserAddress
from app.schemas import ContactInfo, RegisterFinal, VerifyLoginOTP, UserProfileOut, UserProfileDetailOut, UpdateProfileRequest, Token, AddressCreate, AddressOut
from app.otp_utils import generate_otp_secret, generate_otp, verify_otp
from app.email_utils import send_email
from app.database import get_db 
from app.config import AUTHORIZATION_KEY, SECRET_KEY, ALGORITHM


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def is_email(contact: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', contact))

def generate_random_string(length_min=8, length_max=10):
    length = random.randint(length_min, length_max)
    raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return pbkdf2_sha256.hash(raw_password)

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
        user_type='user',
        email=data.email,
        phone_number=data.phone_number,
        phone_country_code='+91',
        password = generate_random_string(),
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

def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return email

async def get_current_user_object(current_user_email: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(UserProfile).where(UserProfile.email == current_user_email)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/add_address", response_model=AddressOut)
async def add_address(address_data: AddressCreate, current_user: UserProfile = Depends(get_current_user_object), db: AsyncSession = Depends(get_db)):
    new_address = UserAddress(
        address_type=address_data.address_type,
        first_name=address_data.first_name,
        last_name=address_data.last_name,
        phone_number=address_data.phone_number,
        country=address_data.country,
        city=address_data.city,
        area=address_data.area,
        zip_code=address_data.zip_code,
        address=address_data.address,
        user_id=current_user.id
    )
    
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address

@router.get("/address_list", response_model=list[AddressOut])
async def get_address_list(current_user: UserProfile = Depends(get_current_user_object), db: AsyncSession = Depends(get_db)):
    query = select(UserAddress).where(UserAddress.user_id == current_user.id)
    result = await db.execute(query)
    addresses = result.scalars().all()
    return addresses

@router.put("/update_address/{address_id}", response_model=AddressOut)
async def update_address(
    address_id: int,
    address_data: AddressCreate,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    # Check if address exists and belongs to current user
    query = select(UserAddress).where(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    )
    result = await db.execute(query)
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Update address fields
    address.address_type = address_data.address_type
    address.first_name = address_data.first_name
    address.last_name = address_data.last_name
    address.phone_number = address_data.phone_number
    address.country = address_data.country
    address.city = address_data.city
    address.area = address_data.area
    address.zip_code = address_data.zip_code
    address.address = address_data.address
    
    await db.commit()
    await db.refresh(address)
    return address

@router.delete("/delete_address/{address_id}")
async def delete_address(
    address_id: int,
    current_user: UserProfile = Depends(get_current_user_object),
    db: AsyncSession = Depends(get_db)
):
    # Check if address exists and belongs to current user
    query = select(UserAddress).where(
        UserAddress.id == address_id,
        UserAddress.user_id == current_user.id
    )
    result = await db.execute(query)
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    await db.delete(address)
    await db.commit()
    
    return {"message": "Address deleted successfully"}