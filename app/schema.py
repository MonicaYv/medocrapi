from pydantic import BaseModel, EmailStr
from typing import Optional

#base
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None

#registration flow 
#request OTP
class ContactInfo(BaseModel):
    contact: str

class OTPVerify(BaseModel):
    contact: str
    otp: str

#user creation
class UserCreate(BaseModel):
    #name: str
    email: EmailStr
    #number

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class UserRegisterWithOTP(BaseModel):
    name: str
    email: EmailStr
    otp: str
    otp_token: str  