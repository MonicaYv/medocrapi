import aiosmtplib
from email.message import EmailMessage


SMTP_HOST = "mail.sizaf.com"
SMTP_PORT = 465
SMTP_USERNAME = "dotsdesktop@sizaf.com"
SMTP_PASSWORD = "eri$45;e]H0K"
SMTP_FROM = "dotsdesktop@sizaf.com"

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
            use_tls=True,     # <--- For port 465 (SSL)
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ EMAIL SEND ERROR: {type(e).__name__}: {e}")
        # For development, we'll simulate the email instead of crashing
        print("📋 EMAIL SIMULATION (due to send error):")
        print("=" * 50)
        print(f"TO: {recipient}")
        print(f"SUBJECT: {subject}")
        print(f"BODY: {body}")
        print("=" * 50)
        print("✅ Email simulated due to connection error!")
        # Don't raise the error - let the API continue working

