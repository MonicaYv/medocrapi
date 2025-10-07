from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime, date, time
from typing import Optional, List, Literal
from decimal import Decimal

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
    referral_code: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None    

class UserProfileOut(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    age: Optional[int] = None
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
        
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    pan_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    

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
    issue_option_id: int
    description: str
    image: Optional[str] = None
    status: Optional[str] = "open"
    created_by_id: Optional[int] = None
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
    status: str = "pending" # pending, replied, closed
    
# --------------------------------------------
# FAQ
# --------------------------------------------    

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
        from_attributes = True

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

class PostTypeOut(BaseModel):
    id: int
    name: str
    is_active: bool
    class Config:
        from_attributes = True

class DonationOut(BaseModel):
    id: int
    amount: int
    order_id: str
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
    
class NGOPostResponse(BaseModel):
    id: int
    user_id: int
    header: str
    description: str
    tags: Optional[str] = None
    post_type: str

    donation_frequency: str
    target_donation: Decimal
    donation_received: Decimal

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pincode: str

    age_group: Optional[str] = None
    gender: Optional[str] = None
    spending_power: Optional[str] = None

    start_date: date
    end_date: date
    status: str

    creative1: str
    creative2: Optional[str] = None

    views: int
    saved: bool
    last_downloaded: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    ngo_name: str
    ngo_city: Optional[str] = None
    ngo_state: Optional[str] = None
    ngo_country: Optional[str] = None
    ngo_pincode: Optional[str] = None
    ngo_address: Optional[str] = None

    class Config:
        from_attributes = True
        
class DonationBillOut(BaseModel):
    receipt_no: str = Field(..., example="NGO-101")
    date: str = Field(..., example="06-Oct-2025")
    ngo_name: str = Field(..., example="Helping Hands Foundation")
    donor_name: str = Field(..., example="John Doe")
    donor_email: EmailStr = Field(..., example="john@example.com")
    amount_donated: float = Field(..., example=1500.0)
    mode_of_payment: str = Field(..., example="UPI")
    reference_no: Optional[str] = Field(None, example="TXN2025ABC123")
    purpose_of_donation: Optional[str] = Field(None, example="Children’s Education")
    amount_in_words: str = Field(..., example="INR 1500 Only")
    platform_details: dict = Field(..., example={
        "company": "Helping Hands Foundation",
        "gstin": "27AABCC1234D1Z2",
        "address": "45-A, Lajpat Nagar, New Delhi - 110024",
        "email": "john@example.com",
        "phone": "+91-9876543210"
        })

    class Config:
        from_attributes = True

class PlatformBillOut(BaseModel):
    receipt_no: int = Field(..., example=2025)
    payment_date: str = Field(..., example="06-Oct-2025")
    ngo_name: str = Field(..., example="Helping Hands Foundation")
    gst: Optional[float] = Field(0.0, example=270.0)
    amount: float = Field(..., example=1500.0)
    pay_mode: str = Field(..., example="Credit Card")
    finalTotal: str = Field(..., example="1770.00")
    email: EmailStr = Field(..., example="john@example.com")
    platform_details: dict = Field(..., example={
        "company": "Helping Hands Foundation",
        "gstin": "27AABCC1234D1Z2",
        "address": "45-A, Lajpat Nagar, New Delhi - 110024",
        "email": "john@example.com",
        "phone": "+91-9876543210"
        })

    class Config:
        from_attributes = True

class ToggleSavedOut(BaseModel):
    success: bool
    saved: bool
    donation_id: int

    class Config:
        from_attributes = True

class DonationExportItem(BaseModel):
    id: int
    amount: float
    status: Optional[str]
    method: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class DonationExportOut(BaseModel):
    total_items: int
    donations: List[DonationExportItem]

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
    
# --------------------------------------------
# Patients
# --------------------------------------------

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    age: int
    relation: Optional[str] = None

class PatientUpdate(BaseModel):
    model_config = {"extra": "forbid"}  # Optional: reject unknown fields
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    relation: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    gender: str
    age: int
    relation: Optional[str] = None

    class Config:
        from_attributes = True


# --------------------------------------------
# Cart
# --------------------------------------------
class CartItemBase(BaseModel):
    medicine_id: str
    quantity: int = 1
    price: Decimal
    original_price: Optional[Decimal] = None
    prescription_status: Literal["Received", "Pending", "Required"]
    is_generic: Optional[bool] = False

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[Decimal] = None

class CartItemOut(CartItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
# --------------------------------------------
# Wallet
# --------------------------------------------

class WalletAddBalance(BaseModel):
    user_name: str
    amount: Decimal
    order_id: Optional[str] = None

class WalletTransactionOut(BaseModel):
    id: int
    user_id: int
    order_id: Optional[str] = None
    tranx_id: str
    amount: Decimal
    transaction_type: str
    points_earned: Decimal
    current_balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class WalletBalanceOut(BaseModel):
    balance: Decimal
    last_updated: datetime

class WalletHistoryOut(BaseModel):
    transactions: List[WalletTransactionOut]
    total: int

# --------------------------------------------
# Appointments
# --------------------------------------------
class HealthIssueOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SpecializationOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class DoctorAppointmentBase(BaseModel):
    address_id: int
    health_issues: Optional[List[int]] = None
    specialization_ids: Optional[List[int]] = None
    description: Optional[str] = None
    consultation_type: Optional[str] = None   # "clinic_visit" | "home_visit"
    service_type: Optional[str] = None        # "emergency" | "normal"
    preferred_date_time: Optional[datetime] = None
    budget: Optional[float] = None
    status: str = "Pending"  # "Pending", "Confirmed", "Completed", "Cancelled"

class DoctorAppointmentUpdate(BaseModel):
    address_id: Optional[int]
    description: Optional[str]
    consultation_type: Optional[str]
    service_type: Optional[str]
    preferred_date_time: Optional[datetime]
    budget: Optional[float]
    health_issues: Optional[List[int]] = []
    specialization_ids: Optional[List[int]] = []
    
class DoctorAppointmentCreate(DoctorAppointmentBase):
    pass

class DoctorAppointmentResponse(BaseModel):
    id: int
    description: Optional[str]
    consultation_type: Optional[str]
    service_type: Optional[str]
    preferred_date_time: Optional[datetime]
    budget: Optional[float]
    status: str
    created_at: Optional[datetime]

    # Nested objects instead of just IDs
    address: Optional[AddressOut]
    health_issues: List[HealthIssueOut] = []
    specializations: List[SpecializationOut] = []

    class Config:
        from_attributes = True

# --------------------------------------------
# App Settings
# --------------------------------------------

class NotificationSettingsOut(BaseModel):
    inapp_notifications: bool
    email_notifications: bool
    push_notifications: bool
    regulatory_alerts: bool
    promotions_and_offers: bool
    location_notification: bool 
    payment_notifications: bool
    quite_mode: bool
    quite_mode_start_time: Optional[time] = None
    quite_mode_end_time: Optional[time] = None

class NotificationSettingsUpdate(BaseModel):
    inapp_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    regulatory_alerts: Optional[bool] = None
    promotions_and_offers: Optional[bool] = None
    location_notification: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    quite_mode: Optional[bool] = None
    quite_mode_start_time: Optional[time] = None
    quite_mode_end_time: Optional[time] = None

# --------------------------------------------
# Purchase
# --------------------------------------------

class ConcernListOut(BaseModel):
    id: int
    category: str

    class Config:
        from_attributes = True  

class TopSellingCategoryOut(BaseModel):
    id: int
    category: str

    class Config:
        from_attributes = True

class CancelReasonOut(BaseModel):
    id: int
    reason: str

    class Config:
        from_attributes = True