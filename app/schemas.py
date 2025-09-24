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
    promotions_and_offers: Optional[bool] = None
    quite_mode: Optional[bool] = None

# Alias for backward compatibility
UserProfileUpdate = UpdateProfileRequest

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
        from_attributes = True
        # orm_mode = True

# --- For GET /api/issue_option?issue_type_id=1 ---
class IssueOptionBase(BaseModel):
    name: str
    issue_type_id: int

class IssueOptionOut(IssueOptionBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True

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
        # orm_mode = True
        from_attributes = True


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
        # orm_mode = True
        from_attributes = True

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
        # orm_mode = True
        from_attributes = True

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
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class PointsBadgeOut(BaseModel):
    id: int
    name: str
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class CouponHistoryCreate(BaseModel):
    id: Optional[int] = None
    date_claimed: Optional[datetime] = datetime.utcnow()
    expiry_date: datetime
    coupon_id: str
    user_id: int

class CouponHistoryOut(BaseModel):
    id: int
    date_claimed: datetime
    expiry_date: datetime   
    coupon_id: str
    user_id: int

    class Config:
        from_attributes = True

class PointsActionTypeCreate(BaseModel):
    action_type: str
    default_points: int

class PointsActionTypeOut(BaseModel):
    id: int
    action_type: str
    default_points: int

    class Config:
        from_attributes = True

# Reward History Schemas
class RewardHistoryCreate(BaseModel):
    user_id: int
    action_type_id: int
    points: int

class RewardHistoryOut(BaseModel):
    id: int
    user_id: int
    action_type_id: int
    points: int
    timestamp: datetime
    action_type: Optional[PointsActionTypeOut] = None  # For joined queries

    class Config:
        from_attributes = True

# Request schema for reward history API with filters
class RewardHistoryFilter(BaseModel):
    action_type_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

# Doctor Profile Schemas
class DoctorProfileCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    age: int
    specialties: str

class DoctorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    specialties: Optional[str] = None

class DoctorProfileOut(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    gender: str
    age: int
    specialties: str

    class Config:
        from_attributes = True

class HealthIssueOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
    

class DonationTypes(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class DonationPost(BaseModel):
    id: int
    header: str
    description: str
    tags: List[str]

    class Config:
        from_attributes = True

# Donation History Schemas
class DonationOut(BaseModel):
    id: int
    amount: int
    order_id: int
    payment_date: datetime
    gst: int
    platform_fee: int
    amount_to_ngo: int
    transaction_id: str
    payment_method: str
    pan_number: str
    pan_document: str
    payment_status: str
    created_at: datetime
    ngopost_id: int
    user_id: int
    saved: bool

    class Config:
        from_attributes = True

class DonationHistoryFilter(BaseModel):
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

# Donation Bill Schema
class DonationBillOut(BaseModel):
    receipt_no: str
    date: str
    ngo_name: str
    ngo_pan: str = "AABC14567D"
    ngo_80g_reg_no: str = "80G/98765/2023-24"
    ngo_address: str = "45-A, Lajpat Nagar, New Delhi - 110024"
    
    # Donor Details
    donor_name: str
    donor_email: str
    donor_pan: Optional[str] = None
    
    # Payment Details
    amount_donated: int
    mode_of_payment: str
    reference_no: str
    
    # Additional Details
    purpose_of_donation: str
    eligible_for_80g_deduction: bool = True
    amount_in_words: str
    
    # Acknowledgment
    receipt_acknowledgment: str = "This receipt acknowledges that we have received the above-mentioned donation voluntarily. Thank you for your support."
    authorized_signatory: str = "Authorized Signatory"
    organization_name: str = "Jeevan Prakash Foundation"

    class Config:
        from_attributes = True
    