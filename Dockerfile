FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /fma

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p logs media

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations users && python manage.py migrate users && python manage.py makemigrations && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]
#CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
