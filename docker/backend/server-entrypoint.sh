#!/bin/bash

echo "--- Init database ---"
./bin/setup_postgres --no-input

echo
echo "--- Starting web server ---"
./bin/run_django_server