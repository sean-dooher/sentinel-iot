cd /app
dockerize -wait tcp://database:5432
dockerize -wait tcp://redis:6379
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py jenkins --enable-coverage