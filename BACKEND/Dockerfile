# Use an official Python image
FROM python:3.11-slim

# set workdir
WORKDIR /app

# avoid creating .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install system deps required for postgres drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# expose port used by uvicorn
EXPOSE 8000

# runtime entrypoint (runs wait, migrations, then app)
ENTRYPOINT ["/entrypoint.sh"]
