import aiosmtplib
from email.message import EmailMessage
from .config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    EMAIL_USE_TLS,
)


async def send_email(recipient: str, subject: str, body: str):
    print(f"📧 Attempting to send email to: {recipient}")
    print(f"📧 Subject: {subject}")
    print(f"📧 Body: {body}")
    
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    
    print(f"🔗 Connecting to {SMTP_HOST}:{SMTP_PORT} with SSL")
    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            use_tls=EMAIL_USE_TLS,
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ EMAIL SEND ERROR: {type(e).__name__}: {e}")

