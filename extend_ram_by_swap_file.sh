#!/bin/bash

# 1. Создаем пустой файл подкачки размером 512 МБ
sudo dd if=/dev/zero of=/swapfile bs=1M count=512

# 2. Выставляем безопасные права (только для системы)
sudo chmod 600 /swapfile

# 3. Форматируем этот файл под область подкачки
sudo mkswap /swapfile

# 4. Подключаем файл подкачки
sudo swapon /swapfile

# 5. Добавляем в автозагрузку
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

