#!/bin/bash
set -e

echo "Подтягиваем свежий обновления..."
git pull

echo "Пересобираем и запускаем контейнеры в фоне..."
docker compose up -d --build

echo "Применяем миграции (если изменились модели)..."
docker compose exec web python manage.py migrate

echo "Проверяем статус контейнеров..."
docker compose ps

echo "🎉 Обновление успешно развернуто! :)"