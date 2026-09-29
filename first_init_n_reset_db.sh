#!/bin/bash

if [ -f .env ]; then
    export $(grep -v '^#' .env | sed 's/\r$//' | xargs)
else
    echo "Ошибка: Файл .env не найден!"
    exit 1
fi

set -e

docker compose down
sudo rm -rf ./db/*

mkdir -p logs media

docker compose build --no-cache

echo "Ожидаем инициализацию MySQL..."
docker compose up -d db

echo "Применяем миграции базы данных из репозитория..."
docker compose run --rm web sh -c "python manage.py migrate users && python manage.py migrate"

echo "Поднимаем весь проект..."
echo "Ожидаем полную готовность веб-сервера..."
docker compose up -d

echo "Настраиваем стили для NGINX..."
sleep 5
docker compose exec -T web python manage.py collectstatic --noinput

echo "Создаем группы Tenant и Landlord с соответствующими правами..."
sleep 5
docker compose exec -T web python manage.py create_groups

echo "Выдаем полные права пользования на MySQL пользователю ${DB_USER}..."
sleep 5
docker compose exec db mysql -u root -p"${DB_ROOT_PASSWORD}" -e "GRANT ALL PRIVILEGES ON \
test_${DB_NAME}.* TO '${DB_USER}'@'%'; FLUSH PRIVILEGES;"

echo "Синхронизируем расписание административных задач в системном Cron..."
sleep 2
DOCKER_PATH=$(which docker)
CURRENT_PATH=$PATH

cat <<FMA_EOF > fma_crontab
PATH=$CURRENT_PATH:/usr/local/bin

0 4 * * * cd /fma && $DOCKER_PATH compose exec -T web python manage.py flushexpiredtokens >> /fma/logs/blacklist_flush_logs.log 2>&1
30 4 * * * cd /fma && $DOCKER_PATH compose exec -T web python manage.py close_expired_bookings >> /fma/logs/close_bookings.log 2>&1
FMA_EOF

crontab fma_crontab

rm fma_crontab

echo "🎯 Cron-планировщик успешно обновлен! Текущие активные задачи:"
crontab -l

echo "Done!! :)"