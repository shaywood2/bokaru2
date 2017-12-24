#!/bin/sh

echo "[`date`] gunicorn server starting"

chdir /usr/local/bokaru/

exec gunicorn bokaru.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=bokaru.settings.prod \
    --workers 3 \
    --bind 0.0.0.0:8080 \
    --log-level=info \
    --log-file=-
