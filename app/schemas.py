from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None

class ContactInfo(BaseModel):
    contact: str

class VerifyLoginOTP(BaseModel):
    contact: str
    otp: str

class RegisterFinal(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    otp: str
    otp_token: str 
    gender: Optional[str] = None
    age: Optional[int] = None

class UserProfileOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    
    class Config:
        from_attributes = True 

class Token(BaseModel):
    access_token: str
    token_type: str