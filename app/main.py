from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="MedoCRM API")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "API is running!"}