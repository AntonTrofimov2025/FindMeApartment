#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose build --no-cache

mkdir -p logs media

docker compose up -d db
echo "Ожидаем инициализацию MySQL..."
sleep 10

docker compose run --rm migrate sh -c "python manage.py makemigrations users && \
 python manage.py makemigrations && python manage.py migrate users && python manage.py migrate"

#docker compose up -d

echo "Настаиваем стили для NGINX"
sleep 3
#docker exec -T fma_web python manage.py collectstatic --noinput

echo "Done!! :)"