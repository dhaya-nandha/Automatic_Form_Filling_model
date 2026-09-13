import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'form_filler.db'}")

# Machine Learning & Embedding Settings
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Matching Confidence Thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.82    # Direct auto-fill
MEDIUM_CONFIDENCE_THRESHOLD = 0.60  # Try inference / rule derivation before flagging

# Canonical Field Schema Definitions & Common Aliases
CANONICAL_SCHEMA = {
    "first_name": ["first name", "given name", "forename", "fname"],
    "last_name": ["last name", "surname", "family name", "lname"],
    "full_name": ["name", "full name", "applicant name", "your name", "candidate name", "first and last name"],
    "email": ["email", "email address", "e-mail", "contact email"],
    "phone": ["phone number", "mobile number", "mobile", "phone", "contact number", "telephone"],
    "dob": ["date of birth", "dob", "birth date", "born on", "date of birth (dd/mm/yyyy)"],
    "age": ["age", "years old"],
    "address": ["address", "residential address", "home address", "street address", "location"],
    "city": ["city", "town"],
    "state": ["state", "province", "region"],
    "zip_code": ["zip code", "postal code", "pincode", "zip"],
    "country": ["country", "nation"],
    "gender": ["gender", "sex"],
    "nationality": ["nationality", "citizenship"],
    "id_number": ["id number", "passport number", "national id", "ssn", "identity card no"],
    "education_degree": ["highest degree", "qualification", "education", "degree", "highest qualification"],
    "university": ["university", "college", "institution", "school"],
    "job_title": ["current role", "job title", "position", "designation"],
    "total_experience_years": ["years of experience", "total experience", "work experience (years)"],
    "technical_skills": ["skills", "technical skills", "technologies", "programming languages"],
    "cgpa": ["cgpa", "percentage / cgpa", "gpa", "score", "marks"],
    "certifications": ["certifications / courses", "certifications", "courses", "certificates"],
    "intermediate_college": ["intermediate college", "junior college", "12th college"],
    "intermediate_marks": ["intermediate marks", "12th marks", "intermediate score", "intermediate percentage"],
    "secondary_school": ["secondary school", "10th school", "school name"],
    "secondary_school_score": ["secondary school score", "10th score", "secondary score", "secondary marks"]
}
