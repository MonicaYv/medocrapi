import pyotp
import binascii

def generate_otp_secret():
    return pyotp.random_base32()

def generate_otp(secret: str) -> str:
    try:
        return pyotp.TOTP(secret).now()
    except (binascii.Error, ValueError) as e:
        print(f"Error generating OTP: {e}")
        return None

def verify_otp(secret: str, otp: str) -> bool:
    try:
        if not secret or not otp:
            return False
        return pyotp.TOTP(secret).verify(otp, valid_window=5)
    except (binascii.Error, ValueError) as e:
        print(f"Error verifying OTP: {e}")
        return False
