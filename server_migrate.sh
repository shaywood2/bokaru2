#!/usr/bin/env bash

# Migrate
python3 /home/vagrant/bokaru/manage.py makemigrations
python3 /home/vagrant/bokaru/manage.py migrate

# Collect static files
python3 /home/vagrant/bokaru/manage.py collectstatic --noinput

# Create superuser (admin/admin)
python3 /home/vagrant/bokaru/manage.py createsu
