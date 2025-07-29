from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, text, BigInteger
from app.database import Base

class UserProfile(Base):
    __tablename__ = 'UserProfile'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    gender = Column(String(16), nullable=True)
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
    phone_number = Column(String, unique=True, index=True, nullable=False)  # Matches phone_num in DB
    otp_secret = Column(String, nullable=True)  # Store OTP secret for future logins
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