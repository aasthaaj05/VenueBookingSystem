import pandas as pd
import uuid
import os
import json
from django.core.management.base import BaseCommand
from gymkhana.models import Venue, Building
from users.models import CustomUser

class Command(BaseCommand):
    help = "Import venues from a file (CSV or Excel) into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the file (CSV or Excel)")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']  # Read file path from arguments

        try:
            # Determine file type and read accordingly
            _, file_extension = os.path.splitext(file_path)
            if file_extension.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_extension.lower() in [".xls", ".xlsx"]:
                df = pd.read_excel(file_path)
            else:
                self.stdout.write(self.style.ERROR("Unsupported file format. Please provide a CSV or Excel file."))
                return

            # Rename columns to match Django model fields
            df.rename(columns={
                'Building Name': 'building_name',
                'No': 'room_number',
                'Class Room Number': 'venue_name',
                'Floor Number': 'floor_number',
                'Capacity': 'capacity',
                'Features': 'facilities',
                'Pictures URL': 'photo_url',
                'Exact Location of the Venue': 'address',
                'Incharge Email': 'incharge_email',
                'Description': 'description'
            }, inplace=True)

            for index, row in df.iterrows():
                # Get or create the building
                building, _ = Building.objects.get_or_create(
                    name=row['building_name'],
                    defaults={'location': row['address']}  # Default location
                )

                # Get department incharge user
                incharge_email = row.get('incharge_email')
                incharge_user = CustomUser.objects.filter(email=incharge_email).first()

                # Convert facilities to a valid JSON format
                try:
                    facilities = json.loads(row['facilities']) if row['facilities'] else []
                except json.JSONDecodeError:
                    facilities = []

                # Create and save venue
                venue = Venue(
                    id=uuid.uuid4(),
                    venue_name=row['venue_name'],
                    description=row.get('description', ''),
                    photo_url=row.get('photo_url', ''),
                    capacity=row['capacity'],
                    address=row['address'],
                    facilities=facilities,  # Store as JSON
                    department_incharge=incharge_user,
                    building=building,  # ForeignKey relation
                    floor_number=row.get('floor_number'),
                    room_number=row.get('room_number', '')
                )
                venue.save()
                print(f"Created venue: {venue.venue_name}")

            print("Venue import completed successfully.")

        except Exception as e:
            print("Error importing venues:", e)
