import pandas as pd
import uuid
import os
import json
from django.core.management.base import BaseCommand
from gymkhana.models import Venue, Building
from users.models import CustomUser
from math import isnan
  # Adjust the import paths as per your project

class Command(BaseCommand):
    help = "Import venues from a file (CSV or Excel) into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file (CSV or Excel)")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_extension.lower() in [".xls", ".xlsx"]:
                df = pd.read_excel(file_path)
            else:
                self.stdout.write(self.style.ERROR("Unsupported file format. Please provide a CSV or Excel file."))
                return

            # Rename columns for internal use
            df.rename(columns={
                'Building Name': 'building_name',
                'Floor': 'floor_number',
                'Venue Name': 'venue_name',
                'Class Room/Lab/Seminar Hall': 'class_type',
                'Class Room No/Lab No/Seminar Hall No': 'class_number',
                'D/h': 'depth_or_height',
                'Area (Sqm)': 'area_sqm',
                'Capacity(eg 120, 50)': 'capacity',
                'Features(eg projector, MIC , wifi, etc)': 'facilities',
                'Pictures URL': 'picture_urls',
                'Venue Can be Used for(eg hands-on session, lecture, lab,etc)': 'usage_type',
                'Venue Location(eg  AC 101 is in AC first floor near boat club)': 'venue_location',
                'Department incharge name': 'incharge_name',
                'Department incharge phone number': 'dept_incharge_phone',
                'Department incharge email': 'dept_incharge_email',
                'Department assistant name 1': 'dept_assistant_name1',
                'Department assistant name 2': 'dept_assistant_name2',
                'Campus (North/South)': 'campus'
            }, inplace=True)

            for _, row in df.iterrows():
                # Building
                building, _ = Building.objects.get_or_create(
                    name=row.get('building_name', 'Unknown'),
                    defaults={'location': row.get('venue_location', '')}
                )

                # Incharge User (optional fallback if not found)
                incharge_email = row.get('dept_incharge_email')
                incharge_user = CustomUser.objects.filter(email=incharge_email).first() if incharge_email else None

                # Facilities
                try:
                    facilities = json.loads(row['facilities']) if isinstance(row['facilities'], str) else []
                except Exception:
                    facilities = []

                venue = Venue(
                    id=uuid.uuid4(),
                    venue_name=row.get('venue_name'),
                    description='',
                    photo_url=row.get('picture_urls', ''),
                    capacity= 0 if pd.isna(row['capacity']) else int(row['capacity']),
                    address=row.get('venue_location', ''),
                    facilities=facilities,
                    department_incharge=incharge_user,
                    building=building,
                    floor_number=int(row.get('floor_number')) if pd.notnull(row.get('floor_number')) else 0,
                    room_number=row.get('class_number', ''),
                    class_type=row.get('class_type', ''),
                    class_number=row.get('class_number', ''),
                    length=float(row.get('Length', 0)) if pd.notnull(row.get('Length')) else 0,
                    depth_or_height=float(row.get('depth_or_height', 0)) if pd.notnull(row.get('depth_or_height')) else 0,
                    area_sqm=float(row.get('area_sqm', 0)) if pd.notnull(row.get('area_sqm')) else 0,
                    usage_type=row.get('usage_type', ''),
                    venue_location=row.get('venue_location', ''),
                    dept_incharge_phone=row.get('dept_incharge_phone', ''),
                    dept_incharge_email=incharge_email,
                    dept_assistant_name1=row.get('dept_assistant_name1', ''),
                    dept_assistant_name2=row.get('dept_assistant_name2', ''),
                    campus=row.get('campus', '')
                )
                venue.save()
                self.stdout.write(self.style.SUCCESS(f"Created venue: {venue.venue_name}"))

            self.stdout.write(self.style.SUCCESS("Venue import completed successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing venues: {e}"))

