#!/bin/bash
set -e

LOG_FILE="/home/ec2-user/server_init.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Запуск инициализации сервера..."

sudo dnf update -y
sudo dnf install -y docker
sudo dnf install -y cronie
sudo systemctl enable --now docker
sudo systemctl enable --now crond

sudo usermod -aG docker ec2-user

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then BUILDX_DOCKER_ARCH="amd64"
else BUILDX_DOCKER_ARCH="arm64"; fi

DOCKER_CLI_PLUGINS_DIR="/usr/libexec/docker/cli-plugins"
sudo mkdir -p $DOCKER_CLI_PLUGINS_DIR

sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$BUILDX_DOCKER_ARCH" -o $DOCKER_CLI_PLUGINS_DIR/docker-compose
sudo chmod +x $DOCKER_CLI_PLUGINS_DIR/docker-compose

sudo curl -SL https://github.com/docker/buildx/releases/download/v0.37.1/buildx-v0.37.1.linux-$BUILDX_DOCKER_ARCH -o $DOCKER_CLI_PLUGINS_DIR/docker-buildx
sudo chmod +x $DOCKER_CLI_PLUGINS_DIR/docker-buildx

sudo systemctl restart docker

sudo dnf install -y git
sudo mkdir -p /fma
cd /fma
git clone https://github.com/AntonTrofimov2025/FindMeApartment.git .
sudo chown -R ec2-user:ec2-user /fma

echo "Удаляем первичный скрипт инициализации..."
sleep 2
rm FmaProjectEC2AWS.sh

echo "Устанавливаем время на сервере на Европа/Берлин..."
sleep 1
sudo timedatectl set-timezone Europe/Berlin
sleep 1

echo "Script worked well! AWS EC2 Server has been successfully deployed! :)"