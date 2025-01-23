#!/bin/bash

echo "Stopping Django development server..."
pkill -f "manage.py runserver"

echo "Stopping Celery worker..."
pkill -f "celery -A zACK worker"

echo "Stopping Redis server..."
sudo service redis-server stop

echo "All services stopped." 