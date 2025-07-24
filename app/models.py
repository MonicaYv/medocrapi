from sqlalchemy import Column, Integer, String, Boolean
from .database import Base
import datetime as DateTime
import time as Time

class User(Base):
    registration_user = ""

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_country_code = Column(String, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    password = Column(String)
    user_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'))
    last_login = Column(DateTime(timezone=True), nullable=True)
    inapp_notifications = Column(Boolean, server_default='true')
    email_notifications = Column(Boolean, server_default='true')
    push_notifications = Column(Boolean, server_default='true')
    regulatory_alerts = Column(Boolean, server_default='true')
    promotions_and_offers = Column(Boolean, server_default='true')
    is_active = Column(Boolean, server_default='true')
    quite_mode = Column(Boolean, server_default='false')
    quite_mode_start_time = Column(Time, nullable=True)
    quite_mode_end_time = Column(Time, nullable=True)
    last_login_ip = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'))