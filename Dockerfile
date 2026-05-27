FROM python:3.9-slim

# Force rebuild - change this timestamp to invalidate cache
LABEL rebuild="2026-05-27-runtime-migrations"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files ONLY (no migrations at build time)
RUN python manage.py collectstatic --noinput

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run migrations at runtime, then seed data, then start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_data && gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]
