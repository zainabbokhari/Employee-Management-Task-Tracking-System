FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Make entrypoint executable
RUN chmod +x ./scripts/entrypoint.sh || true

EXPOSE 8000

CMD ["./scripts/entrypoint.sh"]
