#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

npm install
gulp deploy
python manage.py createcachetable
python manage.py collectstatic --no-input --clear
python manage.py migrate
python manage.py createsuperuser --no-input
python manage.py wagtailsiteupdate hypha.test apply.hypha.test 80
python manage.py runserver 8080
# gunicorn opentech.wsgi:application --reload --daemon --workers 3 --bind 127.0.0.1:8080 --env DJANGO_SETTINGS_MODULE=opentech.settings.dev

exec "$@"