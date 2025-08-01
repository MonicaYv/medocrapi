from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, text, BigInteger, ForeignKey
from app.database import Base

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