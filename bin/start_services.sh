#!/bin/bash

echo "Starting Redis server..."
sudo service redis-server start

echo "Starting Celery worker..."
celery -A zACK worker -l info &

echo "Starting Django development server..."
python manage.py runserver 127.0.0.1:8000 & 