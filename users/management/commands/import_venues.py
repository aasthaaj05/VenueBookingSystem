import pandas as pd
import uuid
import os
import json
from django.core.management.base import BaseCommand
from gymkhana.models import Venue, Building
from users.models import CustomUser
import numpy as np

class Command(BaseCommand):
    help = "Import venues from a file (CSV or Excel) into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file (CSV or Excel)")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() == ".csv":
                df = pd.read_csv(file_path, keep_default_na=False)
            elif file_extension.lower() in [".xls", ".xlsx"]:
                df = pd.read_excel(file_path, keep_default_na=False)
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
                'Campus (North/South)': 'campus',
                'Venue Admin': 'venue_admin',
            }, inplace=True)

            # Drop rows where all values are NaN or empty
            df.replace('', np.nan, inplace=True)
            df.dropna(how='all', inplace=True)

            for _, row in df.iterrows():
                # Skip rows with empty venue_name (assuming it's a required field)
                if pd.isna(row.get('venue_name')) or not str(row.get('venue_name')).strip():
                    continue

                # Building
                building_name = str(row.get('building_name', 'Unknown')).strip()
                if not building_name:
                    building_name = 'Unknown'
                
                building, _ = Building.objects.get_or_create(
                    name=building_name,
                    defaults={'location': str(row.get('venue_location', '')).strip()}
                )

                # Incharge User (optional fallback if not found)
                incharge_email = str(row.get('dept_incharge_email', '')).strip()
                incharge_user = CustomUser.objects.filter(email=incharge_email).first() if incharge_email else None

                # Facilities
                facilities = []
                if not pd.isna(row.get('facilities')) and str(row.get('facilities')).strip():
                    try:
                        facilities = json.loads(str(row['facilities'])) if isinstance(row['facilities'], str) else []
                    except Exception:
                        facilities = []

                # Prepare numeric fields with proper NaN handling
                capacity = 0
                if not pd.isna(row.get('capacity')) and str(row.get('capacity')).strip():
                    try:
                        capacity = int(float(row['capacity']))
                    except (ValueError, TypeError):
                        capacity = 0

                floor_number = 0
                if not pd.isna(row.get('floor_number')) and str(row.get('floor_number')).strip():
                    try:
                        floor_number = int(float(row['floor_number']))
                    except (ValueError, TypeError):
                        floor_number = 0

                area_sqm = 0.0
                if not pd.isna(row.get('area_sqm')) and str(row.get('area_sqm')).strip():
                    try:
                        area_sqm = float(row['area_sqm'])
                    except (ValueError, TypeError):
                        area_sqm = 0.0

                depth_or_height = 0.0
                if not pd.isna(row.get('depth_or_height')) and str(row.get('depth_or_height')).strip():
                    try:
                        depth_or_height = float(row['depth_or_height'])
                    except (ValueError, TypeError):
                        depth_or_height = 0.0

                venue = Venue(
                    id=uuid.uuid4(),
                    venue_name=str(row.get('venue_name', '')).strip(),
                    description='',
                    photo_url=str(row.get('picture_urls', '')).strip(),
                    capacity=capacity,
                    address=str(row.get('venue_location', '')).strip(),
                    facilities=facilities,
                    department_incharge=incharge_user,
                    building=building,
                    floor_number=floor_number,
                    room_number=str(row.get('class_number', '')).strip(),
                    class_type=str(row.get('class_type', '')).strip(),
                    class_number=str(row.get('class_number', '')).strip(),
                    length=float(row.get('Length', 0)) if not pd.isna(row.get('Length')) else 0.0,
                    depth_or_height=depth_or_height,
                    area_sqm=area_sqm,
                    usage_type=str(row.get('usage_type', '')).strip(),
                    venue_location=str(row.get('venue_location', '')).strip(),
                    dept_incharge_phone=str(row.get('dept_incharge_phone', '')).strip(),
                    dept_incharge_email=str(incharge_email).strip(),
                    dept_assistant_name1=str(row.get('dept_assistant_name1', '')).strip(),
                    dept_assistant_name2=str(row.get('dept_assistant_name2', '')).strip(),
                    campus=str(row.get('campus', '')).strip(),
                    venue_admin=str(row.get('venue_admin', '')).strip(),
                )
                
                venue.save()
                self.stdout.write(self.style.SUCCESS(f"Created venue: {venue.venue_name}"))

            self.stdout.write(self.style.SUCCESS(f"Venue import completed successfully. Imported {len(df)} venues."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error importing venues: {str(e)}"))