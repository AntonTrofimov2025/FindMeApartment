#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose build --no-cache

docker compose up -d db
echo "Ожидаем инициализацию MySQL..."
sleep 10

docker compose run --rm migrate sh -c "python manage.py makemigrations users &&
 python manage.py makemigrations && python manage.py migrate users && python manage.py migrate"

echo "Done!! :)"