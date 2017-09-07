#!/usr/bin/env bash

# Migrate
python3 manage.py makemigrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput --settings=bokaru.settings.prod

# Create superuser (admin/admin)
python3 manage.py createsu
