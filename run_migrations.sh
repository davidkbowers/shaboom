#!/bin/bash

# migrate accounts
python manage.py makemigrations accounts
python manage.py migrate accounts

# migrate tenants
python manage.py makemigrations tenants
python manage.py migrate tenants

# migrate videos
python manage.py makemigrations videos
python manage.py migrate videos
