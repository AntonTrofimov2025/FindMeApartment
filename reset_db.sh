#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose -f docker-compose.yml -f docker-compose-with-migrate.yml down
sudo rm -rf ./db/*

docker compose -f docker-compose-with-migrate.yml build --no-cache

mkdir -p logs media

echo "Ожидаем инициализацию MySQL..."
docker compose -f docker-compose-with-migrate.yml up -d db

docker compose -f docker-compose-with-migrate.yml run --rm migrate sh -c "python manage.py makemigrations users && \
 python manage.py makemigrations && python manage.py migrate users && python manage.py migrate"

echo "Поднимаем весь проект..."
echo "Ожидаем полную готовность веб-сервера..."
docker compose -f docker-compose.yml up -d

echo "Настраиваем стили для NGINX..."
sleep 5
docker compose exec -T web python manage.py collectstatic --noinput

echo "Done!! :)"