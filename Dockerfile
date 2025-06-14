# Use Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (not strictly required, but good for Docker compatibility)
EXPOSE 8000

# Use Python runner that respects Railway's dynamic port
CMD ["sh", "-c", "uvicorn api.index:app --host 0.0.0.0 --port $PORT"]
