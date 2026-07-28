#!/bin/sh

uv run manage.py collectstatic --noinput
uv run manage.py migrate
uv run gunicorn labpro.wsgi --bind=0.0.0.0:80
