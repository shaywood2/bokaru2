#!/usr/bin/env bash

# Migrations and static files
python3 /usr/local/bokaru/manage.py makemigrations --settings=bokaru.settings.prod
python3 /usr/local/bokaru/manage.py migrate --settings=bokaru.settings.prod
python3 /usr/local/bokaru/manage.py collectstatic --noinput --settings=bokaru.settings.prod

# Create superuser (admin/admin)=
python3 /usr/local/bokaru/manage.py createadmin --settings=bokaru.settings.prod

# Create products
python3 /usr/local/bokaru/manage.py createproducts --settings=bokaru.settings.prod
