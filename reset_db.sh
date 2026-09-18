#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose build --no-cache

mkdir -p logs media

echo "Ожидаем инициализацию MySQL..."
docker compose up -d db
docker compose wait db --condition service_healthy

docker compose run --rm migrate sh -c "python manage.py makemigrations users && \
 python manage.py makemigrations && python manage.py migrate users && python manage.py migrate"

docker compose up -d

echo "Ожидаем полную готовность веб-сервера..."
docker compose wait web --condition service_healthy

echo "Настраиваем стили для NGINX..."
docker compose exec -T web python manage.py collectstatic --noinput

echo "Done!! :)"