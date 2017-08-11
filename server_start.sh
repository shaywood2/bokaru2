#!/usr/bin/env bash

gunicorn -b 0.0.0.0:8000 bokaru.wsgi
