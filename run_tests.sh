#!/usr/bin/env sh
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379
python3 manage.py makemigrations
python3 manage.py migrate
export TEST_REPORT="TRUE"
python3 manage.py test --noinput
