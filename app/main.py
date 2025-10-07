from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.profile import user_profile, user_auth, user_settings
from app.payments import user_payments
from app.Help_center import help_center
from app.points_rewards import user_points_rewards
from app.patients_doctors import user_doctors, user_patients
from app.donation import user_donation
from app.Purchase import user_purchase, user_cart
from app.Advance import wallet
from app.patients_doctors import appointment

app = FastAPI(title="MedoCRM API")

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory="app"), name="static")

app.include_router(user_auth.router)
app.include_router(user_profile.router)
app.include_router(user_settings.router)
app.include_router(user_payments.router)
app.include_router(help_center.router)
app.include_router(user_points_rewards.router)
app.include_router(user_doctors.router)
app.include_router(user_donation.router)
app.include_router(user_purchase.router)
app.include_router(user_cart.router)
app.include_router(wallet.router)
app.include_router(appointment.router)
app.include_router(user_patients.router)

@app.get("/")
def root():
    return {"message": "API is running!"}