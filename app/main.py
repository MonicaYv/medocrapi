from fastapi import FastAPI
from app.routers import user_auth

app = FastAPI(title="MedoCRM API")

app.include_router(user_auth.router)

@app.get("/")
def root():
    return {"message": "API is running!"}