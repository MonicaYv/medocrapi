import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY", "default-auth-key-change-me")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-me-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Email settings
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

# SMTP settings (commented out for development - causing DNS errors)
# SMTP_HOST = os.getenv("SMTP_HOST", "mail.sizaf.com")
# SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
# SMTP_USERNAME = os.getenv("SMTP_USERNAME", "dotsdesktop@sizaf.com")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "eri$45;e]H0K")
# SMTP_FROM = os.getenv("SMTP_FROM", "dotsdesktop@sizaf.com")

# Alternative SMTP settings for production (when EMAIL_ENABLED=true)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
SMTP_FROM = os.getenv("SMTP_FROM", "your_email@gmail.com")
