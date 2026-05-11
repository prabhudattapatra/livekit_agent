# Use official Python lightweight image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# (libpq-dev is sometimes helpful for psycopg, but we use psycopg-binary so it should be fine. 
# Installing standard CA certs just in case)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the backend application code
# (Assuming your frontend is in the frontend/ folder, we ignore it via .dockerignore)
COPY . .

# Run the agent in production mode
CMD ["python", "agent.py", "start"]
