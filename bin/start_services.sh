#!/bin/bash

echo "Starting Redis server..."
sudo service redis-server start

echo "Starting Celery worker..."
nohup celery -A zACK worker -l info &

echo "Starting Django development server..."
nohup python manage.py runserver 127.0.0.1:8000 & 