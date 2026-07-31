# Use official Python runtime
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the backend requirements file
COPY backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/ backend/

# Set working directory to backend so relative paths (like ./data) work
WORKDIR /app/backend

# Expose port 7860 (Required for Hugging Face Spaces)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
