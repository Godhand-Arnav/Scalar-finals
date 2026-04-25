FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire repo
COPY . /app/

# Install environment as package
RUN pip install --no-cache-dir .

EXPOSE 7860

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]