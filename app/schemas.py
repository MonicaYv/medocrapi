from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, date, time
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class ContactInfo(BaseModel):
    contact: str
    
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
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    pan_number: Optional[str] = None
    profile_photo_path: Optional[str] = None
    referral_code: Optional[str] = None
    email: EmailStr
    class Config:
        from_attributes = True
        
class VerifyLoginOTP(BaseModel):
    contact: str
    otp: str
        
class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    pan_number: Optional[str] = None
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

UserProfileUpdate = UpdateProfileRequest

class AddressBase(BaseModel):
    address_type: str
    first_name: str
    last_name: Optional[str] = None
    phone_number: str
    country: str
    city: str
    state: str
    pincode: str
    address: str

class AddressCreate(AddressBase):
    pass

class AddressOut(AddressBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------
# Help Center 
# --------------------------------------------

class IssueTypeBase(BaseModel):
    name: str

class IssueTypeOut(IssueTypeBase):
    id: int
    class Config:
        from_attributes = True
        
class IssueOptionBase(BaseModel):
    name: str
    issue_type_id: int
        
class IssueOptionOut(IssueOptionBase):
    id: int
    class Config:
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
        from_attributes = True
        
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

# --------------------------------------------
# Payments
# --------------------------------------------

class PaymentMethodCreate(BaseModel):
    card_holder_name: str
    card_number_masked: str 
    card_type: str
    expiry_month: int
    expiry_year: int
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

# --------------------------------------------
# Donation
# --------------------------------------------

class DonationTypes(BaseModel):
    id: int
    name: str
    is_active: bool
    class Config:
        from_attributes = True

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

class DonationBillOut(BaseModel):
    receipt_no: str
    date: str
    ngo_name: str
    ngo_pan: str = "AABC14567D"  # Static for now
    ngo_80g_reg_no: str = "80G/98765/2023-24"  # Static for now
    ngo_address: str = "45-A, Lajpat Nagar, New Delhi - 110024"  # Static for now
    donor_name: str
    donor_email: str
    donor_pan: Optional[str] = None
    amount_donated: int
    mode_of_payment: str
    reference_no: str
    purpose_of_donation: str
    eligible_for_80g_deduction: bool = True
    amount_in_words: str
    receipt_acknowledgment: str = "This receipt acknowledges that we have received the above-mentioned donation voluntarily. Thank you for your support."
    authorized_signatory: str = "Authorized Signatory"
    organization_name: str = "Jeevan Prakash Foundation"  # Static for now
    class Config:
        from_attributes = True
    
    
# --------------------------------------------
# Points and Badges
# --------------------------------------------

class PointsActionTypeOut(BaseModel):
    id: int
    action_type: str
    default_points: int

    class Config:
        from_attributes = True

class PointsBadgeOut(BaseModel):
    id: int
    name: str
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    class Config:
        from_attributes = True


# --------------------------------------------
# Couupons and Rewards
# --------------------------------------------

class CouponHistoryOut(BaseModel):
    id: int
    date_claimed: datetime
    expiry_date: datetime   
    coupon_id: str
    user_id: int

    class Config:
        from_attributes = True
        
class RewardHistoryOut(BaseModel):
    id: int
    user_id: int
    action_type_id: int
    points: int
    timestamp: datetime
    action_type: Optional[PointsActionTypeOut] = None  # For joined queries
    class Config:
        from_attributes = True

class RewardHistoryResponse(BaseModel):
    reward_history: List[RewardHistoryOut]
    total_points: int
    filtered_total_points: int 

# --------------------------------------------
# Doctors
# --------------------------------------------

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
        
class DoctorAppointmentOut(BaseModel):
    id: int
    doctor_id: str
    name: str
    specialization: Optional[str]
    experience_years: Optional[int]
    gender: Optional[str]
    rating: Optional[float]
    order_id: str
    appointment_date: date
    appointment_start_time: time
    appointment_end_time: time
    created_at: Optional[datetime]
    location: Optional[str]
    distance_km: Optional[float]
    travel_time_mins: Optional[int]
    clinic_fee: Optional[float]
    home_fee: Optional[float]
    status: str

    class Config:
        orm_mode = True