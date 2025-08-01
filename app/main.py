from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import user_auth

app = FastAPI(title="MedoCRM API")

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory="app"), name="static")

app.include_router(user_auth.router)

@app.get("/")
def root():
    return {"message": "API is running!"}