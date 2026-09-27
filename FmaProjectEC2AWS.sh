#!/bin/bash

sudo dnf update -y
sudo dnf install -y docker
sudo dnf install -y cronie
sudo systemctl enable --now docker
sudo systemctl enable --now crond


sudo usermod -aG docker ec2-user

# Download for x86_64 architecture 
DOCKER_CLI_PLUGINS_DIR="/usr/libexec/docker/cli-plugins"
sudo mkdir -p $DOCKER_CLI_PLUGINS_DIR

sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o $DOCKER_CLI_PLUGINS_DIR/docker-compose
sudo chmod +x $DOCKER_CLI_PLUGINS_DIR/docker-compose

sudo curl -SL https://github.com/docker/buildx/releases/download/v0.25.0/buildx-v0.25.0.linux-amd64 -o $DOCKER_CLI_PLUGINS_DIR/docker-buildx
sudo chmod +x $DOCKER_CLI_PLUGINS_DIR/docker-buildx

sudo systemctl restart docker

sudo dnf install -y git
sudo mkdir -p /fma
cd /fma || exit 1
git clone https://github.com/AntonTrofimov2025/FindMeApartment.git .
sudo chown -R ec2-user:ec2-user /fma