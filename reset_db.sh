#!/bin/bash

sudo find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker compose down
sudo rm -rf ./db/*

docker compose build --no-cache

echo "Done!! :)"