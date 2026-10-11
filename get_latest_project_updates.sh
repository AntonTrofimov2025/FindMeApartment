#!/bin/bash
set -e

echo "Подтягиваем свежие обновления..."
git pull

echo "Пересобираем и запускаем контейнеры в фоне..."
docker compose up -d --build

echo "Применяем миграции (если изменились модели)..."
docker compose exec web python manage.py migrate

echo "Компилируем переводы..."
docker compose exec web python manage.py compilemessages

echo "Проверяем статус контейнеров..."
docker compose ps

echo "🎉 Обновление успешно развернуто! :)"