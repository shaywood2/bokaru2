#!/usr/bin/env bash

# Create log folder
mkdir -p /usr/local/bokaru/logs/

# Install updates
sudo apt-get update

# Install dependencies
sudo apt-get install -y supervisor
sudo apt-get install -y nginx
sudo apt-get install -y python3-pip
sudo apt-get install -y libmemcached-dev
sudo apt-get install -y postgis postgresql-9.5-postgis-2.2
sudo apt-get install -y libjpeg8
sudo apt-get install -y zlib1g
sudo apt-get install -y zlib1g-dev libssl-dev python-dev build-essential

# Install certificate dependencies
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:certbot/certbot
sudo apt-get update
sudo apt-get install -y certbot

# Upgrade pip and install Python dependencies
sudo -H pip3 install --upgrade pip
sudo -H pip3 install -r /usr/local/bokaru/requirements/common.txt
sudo -H pip3 install -r /usr/local/bokaru/requirements/prod.txt

# Copy gunicorn configs
sudo cp /usr/local/bokaru/configs/prod/gunicorn_bokaru.sh /usr/local/bin/gunicorn_bokaru.sh
sudo chmod +x /usr/local/bin/gunicorn_bokaru.sh
sudo cp /usr/local/bokaru/configs/prod/supervisor_gunicorn_bokaru.conf /etc/supervisor/conf.d
sudo supervisorctl reread
sudo supervisorctl update

# Copy Nginx configs
sudo cp /usr/local/bokaru/configs/prod/nginx.conf /etc/nginx/nginx.conf
sudo cp /usr/local/bokaru/configs/prod/nginx_bokaru.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx_bokaru.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Set up python alias and database URL
echo "alias python=python3" >> ~/.bashrc
