# ======================
# Agent-ERP Backend API
# ======================
FROM python:3.13-slim

# System deps (optional but helpful for debugging/health)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY backend /app/backend
COPY data /app/data

# Expose API port
EXPOSE 8000

# Environment: point to the SQLite in the container
ENV APP_ENV=prod
ENV SQLITE_PATH=/app/data/erp_sample.db

# Start the API
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
