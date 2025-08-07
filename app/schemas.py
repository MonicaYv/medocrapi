from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from typing import Optional, List

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


#help center

class IssueTypeBase(BaseModel):
    name: str

class IssueTypeOut(IssueTypeBase):
    id: int

    class Config:
        orm_mode = True

# --- For GET /api/issue_option?issue_type_id=1 ---
class IssueOptionBase(BaseModel):
    name: str
    issue_type_id: int

class IssueOptionOut(IssueOptionBase):
    id: int

    class Config:
        orm_mode = True

class SupportTicketBase(BaseModel):
    description: str
    image: Optional[str] = None
    status: Optional[str] = "open"
    created_by_id: int
    issue_option_id: int
    user_id: int
    assigned_to: Optional[int] = None

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketOut(SupportTicketBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ChatSupportCreate(BaseModel):
    chat_session_id: str
    user_id: int
    message: str
    sender_type: str  # 'user' or 'agent'
    sender_id: Optional[int] = None
    session_status: Optional[str] = "active"
    priority: Optional[str] = "normal"
    message_type: Optional[str] = "text"
    attachment_url: Optional[str] = None

class ChatSupportOut(ChatSupportCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    is_read: bool

    class Config:
        orm_mode = True

class FAQBase(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    profile_type: Optional[str] = None
    user_id: Optional[int] = None

class FAQOut(FAQBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FAQSearch(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    profile_type: Optional[str] = None


# Email Support Schemas
class EmailSupportCreate(BaseModel):
    subject: str
    message: str
    priority: Optional[str] = "normal"

class EmailSupportOut(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    email: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmailSupportUpdateStatus(BaseModel):
    status: str  # pending, replied, closed


# Payment Methods Schemas
class PaymentMethodCreate(BaseModel):
    card_holder_name: str
    card_number_masked: str  # e.g., "**** **** **** 1234"
    card_type: str  # visa, mastercard, amex, etc.
    expiry_month: int  # 1-12
    expiry_year: int  # 2025, 2026, etc.
    is_default: Optional[bool] = False
    payment_gateway: Optional[str] = "stripe"

class PaymentMethodUpdate(BaseModel):
    card_holder_name: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: Optional[bool] = None

class PaymentMethodOut(BaseModel):
    id: int
    user_id: int
    card_holder_name: str
    card_number_masked: str
    card_type: str
    expiry_month: int
    expiry_year: int
    is_default: bool
    payment_gateway: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Points and Badges Schemas

class PointsBadgeCreate(BaseModel):
    name: str