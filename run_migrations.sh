#!/bin/bash

# migrate accounts
python manage.py makemigrations accounts
python manage.py migrate accounts

python manage.py migrate contenttypes

python manage.py migrate admin

# migrate tenants
python manage.py makemigrations tenants
python manage.py migrate tenants

python manage.py migrate_schemas

# migrate studio
python manage.py makemigrations studio
python manage.py migrate studio

# migrate videos
python manage.py makemigrations videos
python manage.py migrate videos

