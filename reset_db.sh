#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose up -d db
echo "Ожидаем инициализацию MySQL..."
sleep 10

docker compose run --rm migrate python manage.py makemigrations users
docker compose run --rm migrate python manage.py migrate users

docker compose build --no-cache