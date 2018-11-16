#!/usr/bin/env sh
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379

cd /sentinel && python manage.py runworker default

