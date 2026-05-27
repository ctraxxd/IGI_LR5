FROM python:3.9-slim

# Force rebuild - change this timestamp to invalidate cache
LABEL rebuild="2026-05-27-migrations-fix"

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

# Collect static files
RUN python manage.py collectstatic --noinput

# ALWAYS run migrations (don't cache this step)
RUN python manage.py migrate --noinput 2>&1 | tee /tmp/migrate.log && cat /tmp/migrate.log

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
