import pandas as pd
import uuid
import os
from django.core.management.base import BaseCommand
from gymkhana.models import Venue
from users.models import CustomUser

class Command(BaseCommand):
    help = "Import venues from a file (CSV or Excel)"

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
                'Class Room/Lab': 'venue_name',
                'Class Room Number': 'room_number',
                'Capacity': 'capacity',
                'Features': 'facilities',
                'Pictures URL': 'photo_url',
                'Exact Location of the Venue': 'address'
            }, inplace=True)

            for index, row in df.iterrows():
                incharge_email = row.get('incharge_email')
                incharge_user = CustomUser.objects.filter(email=incharge_email).first()

                venue = Venue(
                    id=uuid.uuid4(),
                    venue_name=row['venue_name'],
                    description=row.get('description', ''),
                    photo_url=row.get('photo_url', ''),
                    capacity=row['capacity'],
                    address=row['address'],
                    facilities=row.get('facilities', '[]'),  # JSON data
                    department_incharge=incharge_user,
                    building_name=row.get('building_name', ''),
                    room_number=row.get('room_number', '')
                )
                venue.save()
                print(f"Created venue: {venue.venue_name}")

            print("Venue import completed successfully.")

        except Exception as e:
            print("Error importing venues:", e)
