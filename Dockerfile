FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    lsb-release \
    fonts-liberation \
    xdg-utils \
    wget \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*\
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium, etc.)
RUN playwright install --with-deps

# Copy the rest of the app
COPY . .

# Expose port for Render
EXPOSE 8000

# Ensure /app is in PYTHONPATH when running scripts
RUN PYTHONPATH=/app python scripts/scrape_discourse.py && \
    PYTHONPATH=/app python scripts/build_vector_store.py


# Add PYTHONPATH so FastAPI can find modules
ENV PYTHONPATH=/app

# Run Uvicorn on the port Railway provides, fallback to 8000
CMD uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8000}
