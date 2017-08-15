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
