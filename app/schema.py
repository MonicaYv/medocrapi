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

#final user creation
class UserCreateFinal(BaseModel):
    password: str
    name: str 
    user_type: str = "ngo"

# user table
class UserOut(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    user_type: str
    name: str

    class Config:
        orm_mode = True 