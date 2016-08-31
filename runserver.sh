#!/bin/bash

clear
echo "Starting a server at localhost:8000"
python ./mysite/manage.py runserver 0.0.0.0:8000
