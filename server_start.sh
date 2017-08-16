#!/usr/bin/env bash

gunicorn --env DJANGO_SETTINGS_MODULE=bokaru.settings.prod -b unix:/tmp/gunicorn.sock bokaru.wsgi