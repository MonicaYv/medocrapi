from sqlalchemy import (
    Column,
    Integer, DECIMAL,
    String, Text,
    Boolean, Enum,
    DateTime, TIMESTAMP,
    Date, Time,
    ForeignKey,
    JSON, Enum,
    Numeric,
)
import enum
from datetime import time, datetime, date
from sqlalchemy import func
from app.database import Base
import enum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "registration_user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(254), unique=True, nullable=False)
    phone_country_code = Column(String(8), nullable=True)
    phone_number = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    user_type = Column(String(32), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    inapp_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    regulatory_alerts = Column(Boolean, default=True)
    promotions_and_offers = Column(Boolean, default=True)
    quite_mode = Column(Boolean, default=False)
    quite_mode_start_time = Column(Time, nullable=True, default=time(22, 0))
    quite_mode_end_time = Column(Time, nullable=True, default=time(6, 0))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String, nullable=True, default=None)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    donations = relationship("Donation", back_populates="user", cascade="all, delete")
    claimed_coupons = relationship("CouponHistory", back_populates="user", cascade="all, delete")
    coupons = relationship("Coupon", back_populates="advertiser", cascade="all, delete")
    points_history = relationship("RewardHistory", back_populates="user", cascade="all, delete")

class UserProfile(Base):
    __tablename__ = "registration_userprofile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String(16), nullable=True)
    pan_number = Column(String(32), nullable=True)
    profile_photo_path = Column(String(255), nullable=True)
    referral_code = Column(String(64), nullable=True)
    otp = Column(String(16), nullable=True)
    
    user = relationship("User", back_populates="profile")
    addresses = relationship("UserAddress", back_populates="user_profile", cascade="all, delete")

class UserAddress(Base):
    __tablename__ = "registration_useraddress"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("registration_userprofile.id", ondelete="CASCADE"))
    address_type = Column(String(64), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=False)
    country = Column(String(128), nullable=False)
    city = Column(String(128), nullable=False)
    state = Column(String(128), nullable=False)
    pincode = Column(String(20), nullable=False)
    address = Column(String, nullable=False)
    
    user_profile = relationship("UserProfile", back_populates="addresses")


class IssueType(Base):
    __tablename__ = "support_issuetype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    options = relationship("IssueOption", back_populates="issue_type", cascade="all, delete")

    def __str__(self):
        return self.name

class IssueOption(Base):
    __tablename__ = "support_issueoption"
    __table_args__ = (
        # unique together constraint
        {"sqlite_autoincrement": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    issue_type_id = Column(Integer, ForeignKey("support_issuetype.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)

    issue_type = relationship("IssueType", back_populates="options")
    tickets = relationship("SupportTicket", back_populates="issue_option")

    def __str__(self):
        return f"{self.issue_type.name} - {self.name}"


class SupportTicket(Base):
    __tablename__ = "support_supportticket"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"))
    created_by_id = Column(Integer, ForeignKey("registration_user.id", ondelete="SET NULL"), nullable=True)
    issue_option_id = Column(Integer, ForeignKey("support_issueoption.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    status = Column(String(20), default="1")  # could be Enum later
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    assigned_to = Column(String(10), nullable=True)

    user = relationship("User", foreign_keys=[user_id], backref="submitted_tickets")
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_tickets")
    issue_option = relationship("IssueOption", back_populates="tickets")
    chat_messages = relationship("TicketChatMessage", back_populates="ticket", cascade="all, delete")

    def ticket_id(self):
        return f"{10000000 + self.id}"

    def __str__(self):
        creator = self.created_by.email if self.created_by else "Unknown"
        return f"{self.ticket_id()} - {self.issue_option} - by {creator}"


CHATBOT_USER_TYPE_CHOICES = ["advertiser", "client", "ngo", "provider", "user"]

class ChatSupport(Base):
    __tablename__ = "support_chat"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id"))
    message = Column(Text, nullable=False)
    sender_type = Column(String, nullable=False)
    sender_id = Column(Integer, nullable=True)
    session_status = Column(String, default="active")
    priority = Column(String, default="normal")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_read = Column(Boolean, default=False)
    message_type = Column(String, default="text")
    attachment_url = Column(String, nullable=True)

class ChatOptionGroup(Base):
    __tablename__ = "support_chatoptiongroup"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String(32), unique=True, nullable=False)
    options_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return f"Chat Content for {self.user_type} (Active: {self.is_active})"


class EmailSupport(Base):
    __tablename__ = "support_email"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id"))
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, default="pending")
    priority = Column(String, default="normal")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    user = relationship("User")
    
class FAQ(Base):
    __tablename__ = "account_faq"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    profile_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = Column(Integer, ForeignKey("registration_user.id"))  
    user = relationship("User") 
    

class UserManagement(Base):
    __tablename__ = "support_usermanagement"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    status = Column(String(20), default="1")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return f"{self.name} - {self.status}"


class TicketChatMessage(Base):
    __tablename__ = "support_ticketchatmessage"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_supportticket.id", ondelete="CASCADE"))
    sender_id = Column(Integer, ForeignKey("registration_user.id", ondelete="SET NULL"), nullable=True)
    sender_type = Column(String(10), default="user")
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    ticket = relationship("SupportTicket", back_populates="chat_messages")
    sender = relationship("User", backref="sent_ticket_messages")
    
    
class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id"))
    card_holder_name = Column(String, nullable=False)
    card_number_masked = Column(String, nullable=False)
    card_type = Column(String, nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False)
    payment_gateway = Column(String, default="razorpay")  
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("User")
    

class PaymentMethodEnum(str, enum.Enum):
    UPI = "UPI"
    Card = "Card"
    NetBanking = "NetBanking"
    Wallet = "Wallet"
    Other = "Other"


class PaymentStatusEnum(str, enum.Enum):
    Success = "Success"
    Failed = "Failed"


class Donation(Base):
    __tablename__ = "donate_donation"

    id = Column(Integer, primary_key=True, index=True)
    ngopost_id = Column(Integer, ForeignKey("ngopost_ngopost.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    order_id = Column(String(64), unique=True, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    gst = Column(DECIMAL(12, 2), nullable=True)
    platform_fee = Column(DECIMAL(12, 2), nullable=True)
    amount_to_ngo = Column(DECIMAL(12, 2), nullable=True)
    transaction_id = Column(String(64), unique=True, nullable=True)
    payment_method = Column(Enum(PaymentMethodEnum), default=PaymentMethodEnum.UPI, nullable=False)
    pan_number = Column(String(32), nullable=True)
    pan_document = Column(String(255), nullable=True)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.Success, nullable=False)
    saved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    ngopost = relationship("NGOPost", back_populates="donations")
    user = relationship("User", back_populates="donations")

    def __str__(self):
        return f"Donation by {self.user_id} to post {self.ngopost_id} - {self.amount}"
    
    
class DonationFrequencyEnum(str, enum.Enum):
    ONETIME = "One-time"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    
class CountryOption(Base):
    __tablename__ = "ngopost_countryoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    states = relationship("StateOption", back_populates="country")
    
class StateOption(Base):
    __tablename__ = "ngopost_stateoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey("ngopost_countryoption.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)

    country = relationship("CountryOption", back_populates="states")
    cities = relationship("CityOption", back_populates="state")
    
class CityOption(Base):
    __tablename__ = "ngopost_cityoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("ngopost_stateoption.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)

    state = relationship("StateOption", back_populates="cities")
    pincodes = relationship("PincodeOption", back_populates="city")
    
class AgeOption(Base):
    __tablename__ = "ngopost_ageoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
class GenderOption(Base):
    __tablename__ = "ngopost_genderoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
class SpendingPowerOption(Base):
    __tablename__ = "ngopost_spendingpoweroption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


class PostStatusEnum(str, enum.Enum):
    ONGOING = "Ongoing"
    CLOSED = "Closed"
    PAUSED = "Paused"

class NGOPost(Base):
    __tablename__ = "ngopost_ngopost"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"), nullable=False)

    header = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True)

    post_type_id = Column(Integer, ForeignKey("ngopost_posttypeoption.id", ondelete="SET NULL"), nullable=True)
    donation_frequency = Column(Enum(DonationFrequencyEnum), default=DonationFrequencyEnum.ONETIME, nullable=False)

    target_donation = Column(DECIMAL(12, 2), nullable=False)
    donation_received = Column(DECIMAL(12, 2), default=0.00)

    country_id = Column(Integer, ForeignKey("ngopost_countryoption.id", ondelete="SET NULL"), nullable=True)
    state_id = Column(Integer, ForeignKey("ngopost_stateoption.id", ondelete="SET NULL"), nullable=True)
    city_id = Column(Integer, ForeignKey("ngopost_cityoption.id", ondelete="SET NULL"), nullable=True)

    pincode = Column(String(10), nullable=False)

    age_group_id = Column(Integer, ForeignKey("ngopost_ageoption.id", ondelete="SET NULL"), nullable=True)
    gender_id = Column(Integer, ForeignKey("ngopost_genderoption.id", ondelete="SET NULL"), nullable=True)
    spending_power_id = Column(Integer, ForeignKey("ngopost_spendingpoweroption.id", ondelete="SET NULL"), nullable=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(Enum(PostStatusEnum), default=PostStatusEnum.ONGOING, nullable=False)

    creative1 = Column(String(255), nullable=False)
    creative2 = Column(String(255), nullable=True)

    views = Column(Integer, default=0)
    saved = Column(Boolean, default=False)
    last_downloaded = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="ngo_posts")
    post_type = relationship("DonationTypes", back_populates="posts")
    donations = relationship("Donation", back_populates="ngopost", cascade="all, delete")    

class DonationTypes(Base):
    __tablename__ = "ngopost_posttypeoption"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    posts = relationship("NGOPost", back_populates="post_type")

class PointsBadge(Base):
    __tablename__ = "points_pointsbadge"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    min_points = Column(Integer) 
    max_points = Column(Integer, nullable=True)  
    description = Column(String, nullable=True)
    image_url = Column(String(255), nullable=True) 
    
class CategoryOption(Base):
    __tablename__ = "coupon_categoryoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __str__(self):
        return self.name


class BrandOption(Base):
    __tablename__ = "coupon_brandoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __str__(self):
        return self.name


class OfferTypeOption(Base):
    __tablename__ = "coupon_offertypeoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __str__(self):
        return self.name


class PincodeOption(Base):
    __tablename__ = "pincode"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    city_id = Column(Integer, ForeignKey("ngopost_cityoption.id", ondelete="CASCADE"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    city = relationship("CityOption", back_populates="pincodes")

    def __str__(self):
        return self.code

class Coupon(Base):
    __tablename__ = "coupon_coupon"

    id = Column(Integer, primary_key=True, index=True)
    advertiser_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(String(50), unique=True, nullable=False)

    # Dropdown-selected string fields
    category_id = Column(Integer, ForeignKey("coupon_categoryoption.id"), nullable=True)
    brand_name_id = Column(Integer, ForeignKey("coupon_brandoption.id"), nullable=True)
    country_id = Column(Integer, ForeignKey("ngopost_countryoption.id"), nullable=True)
    state_id = Column(Integer, ForeignKey("ngopost_stateoption.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("ngopost_cityoption.id"), nullable=True)
    pincode_id = Column(Integer, ForeignKey("pincode.id"), nullable=True)
    age_group_id = Column(Integer, ForeignKey("ngopost_ageoption.id"), nullable=True)
    gender_id = Column(Integer, ForeignKey("ngopost_genderoption.id"), nullable=True)
    spending_power_id = Column(Integer, ForeignKey("ngopost_spendingpoweroption.id"), nullable=True)
    offer_type_id = Column(Integer, ForeignKey("coupon_offertypeoption.id"), nullable=True)

    # Redemptions and validity
    max_redemptions = Column(Integer, nullable=False)
    validity = Column(Date, nullable=False)

    # Image upload (store path string)
    image = Column(String(255), nullable=True)

    # Metrics
    redeemed_count = Column(Integer, default=0, nullable=False)
    views = Column(Integer, default=0, nullable=False)

    # Financial & Payment Details
    displays_per_coupon = Column(Integer, default=1, nullable=False)
    rate_per_display = Column(DECIMAL(10, 2), default=0, nullable=False)

    class PaymentMethodEnum(str, enum.Enum):
        UPI = "upi"
        GATEWAY = "gateway"
        CARD = "card"

    class PaymentStatusEnum(str, enum.Enum):
        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"

    payment_details = Column(JSON, nullable=True)
    payment_method = Column(Enum(PaymentMethodEnum), default=PaymentMethodEnum.UPI, nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, nullable=False)
    final_paid_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    gst_amount = Column(DECIMAL(10, 2), default=0, nullable=False)

    # Metadata
    saved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    advertiser = relationship("User", back_populates="coupons")
    claims = relationship("CouponHistory", back_populates="coupon", cascade="all, delete-orphan")

    # Computed Properties
    @property
    def coupon_balance(self):
        return self.max_redemptions - self.redeemed_count

    @property
    def total_value_before_gst(self):
        return self.max_redemptions * self.displays_per_coupon * float(self.rate_per_display)

    @property
    def gst_value(self):
        return self.total_value_before_gst * 0.18

    @property
    def gross_invoice_amount(self):
        return self.total_value_before_gst + self.gst_value

    @property
    def net_payable(self):
        # Note: advance_received isn’t in your model — if you need it, add the column
        return self.gross_invoice_amount  # placeholder

    @property
    def status(self):
        return "Expired" if self.validity < date.today() else "Active"

    def __str__(self):
        return f"{self.title} ({self.code})"
    
class CouponHistory(Base):
    __tablename__ = "points_couponclaimed"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupon_coupon.id", ondelete="CASCADE"), nullable=False)
    date_claimed = Column(DateTime, default=datetime.now, nullable=False)
    expiry_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="claimed_coupons")
    coupon = relationship("Coupon", back_populates="claims")

class RewardHistory(Base):
    __tablename__ = "points_pointshistory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"), nullable=False)
    action_type_id = Column(Integer, ForeignKey("points_pointsactiontype.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="points_history")
    action_type = relationship("PointsActionType", back_populates="history")

    def __str__(self):
        return f"{self.user.email} - {self.action_type.action_type} - {self.points} pts"

class PointsActionType(Base):
    __tablename__ = "points_pointsactiontype"
    
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(32), unique=True, nullable=False)  # choices handled at app level
    default_points = Column(Integer, default=0, nullable=False)

    history = relationship("RewardHistory", back_populates="action_type", cascade="all, delete")

    def __str__(self):
        return f"{self.action_type} - {self.default_points} pts"
    

class DoctorProfile(Base):
    __tablename__ = "doctor_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    specialties = Column(String, nullable=False)

    user = relationship("User")
    
class HealthIssues(Base):
    __tablename__ = "health_issues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
class DoctorAppointment(Base):
    __tablename__ = "doctor_appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100))
    experience_years = Column(Integer)
    gender = Column(String(20))
    rating = Column(DECIMAL(2,1))
    order_id = Column(String(50), unique=True, nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_start_time = Column(Time, nullable=False)
    appointment_end_time = Column(Time, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    location = Column(String(255))
    distance_km = Column(DECIMAL(5,2))
    travel_time_mins = Column(Integer)
    clinic_fee = Column(DECIMAL(10,2))
    home_fee = Column(DECIMAL(10,2))
    status = Column(String(20), default="Pending")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    medicine_id = Column(String(24), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    prescription_status = Column(String(20), nullable=True)
    is_generic = Column(Boolean, nullable=True, default=False)
    created_at = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

