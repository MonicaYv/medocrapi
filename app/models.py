from sqlalchemy import (Column, Integer, String, Boolean, DateTime, Date, Time, Text, ForeignKey)
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import DECIMAL, TIMESTAMP, func
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
    quite_mode_start_time = Column(Time, nullable=True)
    quite_mode_end_time = Column(Time, nullable=True)
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
    address_type = Column(String(64), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(128), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    pincode = Column(String(20), nullable=True)
    address = Column(String, nullable=True)
    
    user_profile = relationship("UserProfile", back_populates="addresses")

class IssueType(Base):
    __tablename__ = "support_issuetype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # One-to-many relationship
    options = relationship("IssueOption", back_populates="issue_type")

class IssueOption(Base):
    __tablename__ = "support_issueoption"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    issue_type_id = Column(Integer, ForeignKey("support_issuetype.id"), nullable=False)

    # Many-to-one to IssueType
    issue_type = relationship("IssueType", back_populates="options")

    # One-to-many to SupportTicket
    tickets = relationship("SupportTicket", back_populates="issue_option")  

class SupportTicket(Base):
    __tablename__ = "support_supportticket"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image = Column(String, nullable=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_id = Column(Integer, nullable=True)
    issue_option_id = Column(Integer, ForeignKey("support_issueoption.id"))
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    assigned_to = Column(Integer, nullable=True)

    # Correct relationship to IssueOption
    issue_option = relationship("IssueOption", back_populates="tickets")

class ChatSupport(Base):
    __tablename__ = "support_chat"  # FIXED here ✅

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("UserProfile.id"))
    message = Column(Text, nullable=False)
    sender_type = Column(String, nullable=False)  # 'user' or 'agent'
    sender_id = Column(Integer, nullable=True)
    session_status = Column(String, default="active")  # active, closed, waiting
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    message_type = Column(String, default="text")  # text, image, file
    attachment_url = Column(String, nullable=True)

class FAQ(Base):
    __tablename__ = "account_faq"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    profile_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("UserProfile.id"))  
    # user = relationship("UserProfile", back_populates="faqs")  

class EmailSupport(Base):
    __tablename__ = "support_email"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    email = Column(String, nullable=False)  # User's email
    status = Column(String, default="pending")  # pending, replied, closed
    priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserProfile")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    card_holder_name = Column(String, nullable=False)
    card_number_masked = Column(String, nullable=False)  # e.g., "**** **** **** 1234"
    card_type = Column(String, nullable=False)  # visa, mastercard, amex, etc.
    expiry_month = Column(Integer, nullable=False)  # 1-12
    expiry_year = Column(Integer, nullable=False)  # 2025, 2026, etc.
    is_default = Column(Boolean, default=False)
    payment_gateway = Column(String, default="razorpay")  
    status = Column(String, default="active")  # active, expired, deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("UserProfile")

class PointsBadge(Base):
    __tablename__ = "points_pointsbadge"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    min_points = Column(Integer, nullable=True) 
    max_points = Column(Integer, nullable=True)  
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True) 

class CouponHistory(Base):
    __tablename__ = "points_couponclaimed"
    id = Column(Integer, primary_key=True, index=True)
    date_claimed = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=False)
    coupon_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))

    # Relationship
    user = relationship("UserProfile")

class PointsActionType(Base):
    __tablename__ = "points_pointsactiontypes"
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False, unique=False)
    default_points = Column(Integer, nullable=False)

    # Relationship
    points = relationship("RewardHistory", back_populates="action_type")

class RewardHistory(Base):
    __tablename__ = "points_pointshistory"
    id = Column(Integer, primary_key=True, index=True)
    points = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type_id = Column(Integer, ForeignKey("points_pointsactiontypes.id"))
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))

    # Relationship
    action_type = relationship("PointsActionType", back_populates="points")

class PatientProfile(Base):
    __tablename__ = "patient_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    relation = Column(String, nullable=False)

    # Relationship
    user = relationship("UserProfile")

class DoctorProfile(Base):
    __tablename__ = "doctor_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    specialties = Column(String, nullable=False)

    # Relationship
    user = relationship("UserProfile")

class HealthIssues(Base):
    __tablename__ = "health_issues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
class DonationTypes(Base):
    __tablename__ = "ngopost_posttypeoption"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    # Relationship
    posts = relationship("DonationPost", back_populates="post_type")

class DonationPost(Base):
    __tablename__ = "ngopost_ngopost"
    id = Column(Integer, primary_key=True, index=True)
    header = Column(String, nullable=False)
    description = Column(String, nullable=False)
    tags = Column(String, nullable=True)  # Comma-separated tags
    post_type_id = Column(Integer, ForeignKey("ngopost_posttypeoption.id"))
    donation_frequency = Column(String, nullable=True)
    target_donation = Column(Integer, nullable=False)
    donation_received = Column(Integer, nullable=False, default=0)
    country_id = Column(Integer, nullable=False)
    state_id = Column(Integer, nullable=False)
    city_id = Column(Integer, nullable=False)
    pincode = Column(String, nullable=False)
    age_group_id = Column(Integer, nullable=False)
    gender_id = Column(Integer, nullable=False)
    spending_power_id = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    creative1 = Column(String, nullable=True)
    creative2 = Column(String, nullable=True)
    views = Column(Integer, nullable=False, default=0)
    saved = Column(Boolean, default=False)
    last_downloaded = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))

    # Relationship
    user = relationship("UserProfile")
    post_type = relationship("DonationTypes")
    
class Donation(Base):
    __tablename__ = "donate_donation"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    gst = Column(Integer, nullable=False)
    platform_fee = Column(Integer, nullable=False)
    amount_to_ngo = Column(Integer, nullable=False)
    transaction_id = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    pan_number = Column(String, nullable=False)
    pan_document = Column(String, nullable=False)
    payment_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ngopost_id = Column(Integer, ForeignKey("ngopost_ngopost.id"))
    user_id = Column(Integer, ForeignKey("registration_userprofile.id"))
    saved = Column(Boolean, default=False)

    # Relationship
    user = relationship("UserProfile")
    ngo_post = relationship("DonationPost")

# class DoctorAppointment(Base):
#     __tablename__ = "doctor_appointments"

#     id = Column(Integer, primary_key=True, index=True)
#     doctor_id = Column(String(50), nullable=False)
#     name = Column(String(100), nullable=False)
#     specialization = Column(String(100))
#     experience_years = Column(Integer)
#     gender = Column(String(20))
#     rating = Column(DECIMAL(2,1))
#     order_id = Column(String(50), unique=True, nullable=False)
#     appointment_date = Column(Date, nullable=False)
#     appointment_start_time = Column(Time, nullable=False)
#     appointment_end_time = Column(Time, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     location = Column(String(255))
#     distance_km = Column(DECIMAL(5,2))
#     travel_time_mins = Column(Integer)
#     clinic_fee = Column(DECIMAL(10,2))
#     home_fee = Column(DECIMAL(10,2))
#     status = Column(String(20), default="Pending")