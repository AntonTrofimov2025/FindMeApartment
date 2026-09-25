FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /fma

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application", "--workers", "2", "--access-logfile", "-", \
 "--error-logfile", "-", "--max-requests", "1000", "--max-requests-jitter", "50", "--forwarded-allow-ips", \
 "nginx,fma_nginx"]