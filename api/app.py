from fastapi import FastAPI

from api.routes import router

app = FastAPI(

    title="Student Job Matching API",

    version="1.0.0",

    description="AI-Based Student Job Recommendation System"

)

app.include_router(router)