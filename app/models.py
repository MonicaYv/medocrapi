from sqlalchemy import (
    Column,
    Integer, DECIMAL,
    String, Text,
    Boolean, Enum,
    DateTime, TIMESTAMP,
    Date, Time,
    ForeignKey,
    JSON,
)
import enum
from datetime import time, datetime
from sqlalchemy import func
from app.database import Base
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

    __table_args__ = (
        # unique together
        {"sqlite_autoincrement": True},
    )

    def __str__(self):
        return f"{self.issue_type.name} - {self.name}"


class SupportTicket(Base):
    __tablename__ = "support_supportticket"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_user.id", ondelete="CASCADE"))
    created_by_id = Column(Integer, ForeignKey("registration_user.id", ondelete="SET NULL"), nullable=True)
    issue_option_id = Column(Integer, ForeignKey("support_issueoption.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=False)
    image_path = Column(String(255), nullable=True)
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
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
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
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, default="pending")
    priority = Column(String, default="normal")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    user = relationship("UserProfile")
    
class FAQ(Base):
    __tablename__ = "account_faq"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    profile_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))  
    # user = relationship("UserProfile", back_populates="faqs") 
    

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
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
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
    
    user = relationship("UserProfile")
    

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
    created_at = Column(DateTime, default=datetime.utcnow)

    ngopost = relationship("NGOPost", back_populates="donations")
    user = relationship("User", back_populates="donations")

    def __str__(self):
        return f"Donation by {self.user_id} to post {self.ngopost_id} - {self.amount}"
    
class DonationTypes(Base):
    __tablename__ = "ngopost_posttypeoption"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    posts = relationship("DonationPost", back_populates="post_type")

class PointsBadge(Base):
    __tablename__ = "points_pointsbadge"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    min_points = Column(Integer) 
    max_points = Column(Integer, nullable=True)  
    description = Column(String, nullable=True)
    image_url = Column(String(255), nullable=True) 
    
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
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    specialties = Column(String, nullable=False)

    user = relationship("UserProfile")
    
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