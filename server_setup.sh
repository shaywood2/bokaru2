#!/usr/bin/env bash

# Install updates
sudo apt-get update

# Install dependencies
sudo apt-get install -y python3-pip
sudo apt-get install -y memcached

# Upgrade pip and install Python dependencies
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements/common.txt
sudo pip3 install -r requirements/dev.txt

# Set up python alias and database URL
echo "alias python=python3" >> ~/.bashrc
echo "export DATABASE_URL='postgres://bokaru.ccmerekzzbun.ca-central-1.rds.amazonaws.com/bokaru?user=bokaru&password=bokaru123'" >> ~/.bashrc
echo "export AWS_ACCESS_KEY_ID='AKIAJKZZF54QTZ2FEZ7A'" >> ~/.bashrc
echo "export AWS_SECRET_ACCESS_KEY='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'" >> ~/.bashrc
