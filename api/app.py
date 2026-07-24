from fastapi import FastAPI
from api.routes import router

# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="Student Job Matching Marketplace API",
    version="1.0.0",
    description="""
Student Job Matching System - Task 5

This API provides:

• Company Job Posting
• Student Job Applications
• Automatic AI-Based Job Matching
• Candidate Ranking
• Job Recommendation
• Evaluation Metrics
• Health Monitoring
""",
)

# ==========================================================
# Include All API Routes
# ==========================================================

app.include_router(router)

# ==========================================================
# Root Endpoint
# ==========================================================

@app.get(
    "/",
    tags=["Home"]
)
def home():
    """
    Welcome endpoint.
    """
    return {
        "message": "Student Job Matching Marketplace API",
        "version": "1.0.0",
        "status": "Running"
    }