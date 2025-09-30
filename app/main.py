from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.profile import user_profile, user_auth
from app.payments import user_payments
from app.Help_center import help_center
from app.points_rewards import user_points_rewards
from app.patients_doctors import user_doctors
from app.donation import user_donation
# from app.Purchase import user_purchase


app = FastAPI(title="MedoCRM API")

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory="app"), name="static")

app.include_router(user_auth.router)
app.include_router(user_profile.router)
app.include_router(user_payments.router)
app.include_router(help_center.router)
app.include_router(user_points_rewards.router)
app.include_router(user_doctors.router)
app.include_router(user_donation.router)
# app.include_router(user_purchase.router)

@app.get("/")
def root():
    return {"message": "API is running!"}