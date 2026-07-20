from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Student Job Matching API",
    version="1.0.0",
    description="Task 5 - Marketplace Validation API"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Student Job Matching API is running"
    }