#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose build --no-cache

mkdir -p logs media

echo "Ожидаем инициализацию MySQL..."
docker compose up -d db

docker compose run --rm migrate sh -c "python manage.py makemigrations users && \
 python manage.py makemigrations && python manage.py migrate users && python manage.py migrate"

echo "Поднимаем весь проект..."
echo "Ожидаем полную готовность веб-сервера..."
docker compose up -d

echo "Настраиваем стили для NGINX..."
sleep 5
docker compose exec -T web python manage.py collectstatic --noinput

echo "Done!! :)"