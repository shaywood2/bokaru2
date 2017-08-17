#!/usr/bin/env bash

sudo cp bokaru/configs/prod/bokaru-gunicorn.service /etc/systemd/system/bokaru-gunicorn.service
sudo systemctl start bokaru-gunicorn
sudo systemctl enable bokaru-gunicorn
