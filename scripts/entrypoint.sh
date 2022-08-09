#!/bin/sh

set -e

python manage.py collectstatic --noinput

uwsgi --socket :8000 --module taskapp.wsgi --master --enable-threads
