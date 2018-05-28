#!/bin/bash
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379

python manage.py migrate
python manage.py collectstatic --noinput
exec daphne -b 0.0.0.0 -p 8000 ${PROJECT_NAME}.asgi:channel_layer
