# VenueBookingSystem

To run the portal:

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py import_users user_info.xlsx
python3 manage.py import_buildings Building_info.csv
python3 manage.py import_venues COEP_VenuesInfo_1.xlsx
