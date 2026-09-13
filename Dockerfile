# 24/7 Cloud Dockerfile for FormFill AI (FastAPI + Playwright + Sentence Transformers)

FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port (Render/HuggingFace default: 7860 or 5000)
EXPOSE 7860

# Start Uvicorn Server 24/7
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
