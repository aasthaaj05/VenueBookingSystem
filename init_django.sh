#!/bin/bash

echo "Running makemigrations..."
python3 manage.py makemigrations

echo "Running migrate..."
python3 manage.py migrate

echo "Importing users..."
python3 manage.py import_users user_info.xlsx

echo "Importing buildings..."
python3 manage.py import_buildings Building_info.csv

echo "Importing venues..."
python3 manage.py import_venues Data1.xlsx

echo "All done!"

