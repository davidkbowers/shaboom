FROM python:3.12.3

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install setuptools first
RUN pip install --upgrade pip setuptools

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install development dependencies
COPY requirements.dev.txt .
RUN pip install -r requirements.dev.txt

# Copy project
COPY . .

# Run migrations and collect static files
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
