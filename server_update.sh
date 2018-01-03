#!/usr/bin/env bash

cd /usr/local/bokaru/

# Pull changes from git
sudo git pull

# Migrate DB
sudo python3 manage.py makemigrations --settings=bokaru.settings.prod
sudo python3 manage.py migrate --settings=bokaru.settings.prod

# Collect static files
sudo python3 manage.py collectstatic --noinput --settings=bokaru.settings.prod

# Restart web server
sudo supervisorctl restart gunicorn
