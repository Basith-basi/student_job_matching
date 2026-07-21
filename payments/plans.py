"""
Subscription plans for Student Job Matching System
"""

PLANS = {

    "FREE": {
        "name": "Free Plan",
        "price": 0,
        "applications": 5,
        "job_postings": 1,
        "description": "Limited student applications and one job posting."
    },

    "PREMIUM_STUDENT": {
        "name": "Premium Student",
        "price": 299,
        "applications": -1,     # Unlimited
        "job_postings": 0,
        "description": "Unlimited job applications."
    },

    "COMPANY_BASIC": {
        "name": "Company Basic",
        "price": 999,
        "applications": 0,
        "job_postings": 5,
        "description": "Post up to 5 jobs."
    },

    "COMPANY_PREMIUM": {
        "name": "Company Premium",
        "price": 2999,
        "applications": 0,
        "job_postings": -1,     # Unlimited
        "description": "Unlimited job postings."
    }

}