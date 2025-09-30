import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Mongo DB
MONGO_DATABASE_HOST = os.getenv("MONGO_DATABASE_HOST")
MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")

# Email settings
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"