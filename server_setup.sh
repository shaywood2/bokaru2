#!/usr/bin/env bash

# Install updates
sudo apt-get update

# Install dependencies
sudo apt-get install -y python3-pip
sudo apt-get install -y libmemcached-dev
sudo apt-get install -y libjpeg8
sudo apt-get install -y zlib1g

# Upgrade pip and install Python dependencies
sudo pip3 install --upgrade pip
sudo pip3 install -r requirements/common.txt
sudo pip3 install -r requirements/prod.txt

# Set up python alias and database URL
echo "alias python=python3" >> ~/.bashrc
