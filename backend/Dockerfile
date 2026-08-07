FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for database compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install our streamlined requirements
COPY requirements.txt . 
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code
COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]