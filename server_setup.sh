#!/usr/bin/env bash

# Install updates
sudo apt-get update

# Install dependencies
sudo apt-get install -y postgresql-contrib
sudo apt-get install -y postgis postgresql-9.5-postgis-2.1
sudo apt-get build-dep -y psycopg2
sudo apt-get install -y python3-pip
sudo apt-get install -y memcached
#sudo apt-get install libmemcached-dev

# Upgrade pip and install Python dependencies
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements.txt

# Create Postgres user and DB, install extensions
sudo -u postgres psql -c "CREATE ROLE bokaru WITH LOGIN SUPERUSER PASSWORD 'bokaru123'"
sudo -u postgres psql -c "CREATE DATABASE bokaru WITH OWNER bokaru"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" bokaru

# Set up python alias and database URL
echo "alias python=python3" >> ~/.bashrc
echo "export DATABASE_URL='postgres://localhost/bokaru?user=bokaru&password=bokaru123'" >> ~/.bashrc
