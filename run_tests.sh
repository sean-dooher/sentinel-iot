cd /app
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379
python3 manage.py test