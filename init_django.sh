#!/bin/bash

echo "Running makemigrations..."
python3 manage.py makemigrations

echo "Running migrate..."
python3 manage.py migrate

echo "Importing users..."
python3 manage.py import_users user_info.xlsx

echo "Importing venues..."
python3 manage.py import_venues Venues_Data.xlsx

echo "All done!"
