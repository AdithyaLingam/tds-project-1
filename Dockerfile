FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port for Render
EXPOSE 8000

# Ensure /app is in PYTHONPATH when running scripts
RUN PYTHONPATH=/app python scripts/scrape_discourse.py && \
    PYTHONPATH=/app python scripts/build_vector_store.py

# Run Uvicorn on the port Railway provides, fallback to 8000
CMD uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000}
