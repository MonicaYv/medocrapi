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

class UserProfileDetailOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    pan_card: Optional[str] = None
    profile_photo: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    inapp_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    regulatory_alerts: Optional[bool] = None
    promotions_and_offers: Optional[bool] = None
    quite_mode: Optional[bool] = None
    
    class Config:
        from_attributes = True

class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    pan_card: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    age: Optional[int] = None
    inapp_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    regulatory_alerts: Optional[bool] = None
    promotions_and_offers: Optional[bool] = None
    quite_mode: Optional[bool] = None

class UserAddress(BaseModel):
    address_type: str
    first_name: str
    last_name: str
    phone_number: str
    country: str
    city: str
    area: str
    zip_code: str
    address: str

class AddressCreate(UserAddress):
    pass

class AddressOut(UserAddress):
    id: int

    class Config:   
        from_attributes = True