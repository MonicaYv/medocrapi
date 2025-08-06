from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, text,Text, BigInteger, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class UserProfile(Base):
    __tablename__ = 'UserProfile'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(String(16), nullable=True)
    pan_card = Column(String, nullable=True, unique=True, index=True)
    profile_photo = Column(String, nullable=True) 
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    country = Column(String, nullable=True)
    referral_code = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    email_otp = Column(String, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)  
    otp_secret = Column(String, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'))
    inapp_notifications = Column(Boolean, server_default='true')
    email_notifications = Column(Boolean, server_default='true')
    push_notifications = Column(Boolean, server_default='true')
    regulatory_alerts = Column(Boolean, server_default='true')
    promotions_and_offers = Column(Boolean, server_default='true')
    is_active = Column(Boolean, server_default='true')
    quite_mode = Column(Boolean, server_default='false')
    quite_mode_start_time = Column(Time, nullable=True)
    quite_mode_end_time = Column(Time, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String, nullable=True)

class UserAddress(Base):
    __tablename__ = "UserAddress"

    id = Column(Integer, primary_key=True, index=True)
    address_type = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    country = Column(String)
    city = Column(String)
    area = Column(String)
    zip_code = Column(String)
    address = Column(String)
    user_id = Column(Integer, ForeignKey('UserProfile.id'))


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

