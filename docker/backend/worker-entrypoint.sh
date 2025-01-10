#!/bin/bash

echo "--- Starting Celery Workers ---"
# Concurrent workers is set = 1, change if necessary: --concurrency 1
celery -A ack worker --loglevel=info --concurrency 1 -E
