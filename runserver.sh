#!/bin/sh

python manage.py migrate
gunicorn labpro.wsgi --bind=0.0.0.0:80