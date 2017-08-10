#!/usr/bin/env bash

# Install updates
sudo apt-get update

# Install dependencies
sudo apt-get install -y postgresql-contrib
sudo apt-get install -y postgis postgresql-9.3-postgis-2.1
sudo apt-get build-dep -y psycopg2
sudo apt-get install -y python3-pip
sudo apt-get install -y memcached
#sudo apt-get install libmemcached-dev

# Install Python dependencies
sudo pip3 install -r /home/vagrant/bokaru/requirements.txt

# Create Postgres user and DB, install extensions
sudo -u postgres psql -c "CREATE ROLE bokaru WITH LOGIN SUPERUSER PASSWORD 'bokaru123'"
sudo -u postgres psql -c "CREATE DATABASE bokaru WITH OWNER bokaru"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" bokaru