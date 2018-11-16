#!/usr/bin/env sh
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379

python manage.py migrate
python manage.py collectstatic --noinput

if [ "$DJANGO_DEBUG" = "TRUE" ]; then
    exec daphne -b 0.0.0.0 -p 8000 ${PROJECT_NAME}.asgi:application
else
    exec python3 manage.py runserver 0.0.0.0:8000
fi