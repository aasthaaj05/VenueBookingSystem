import pandas as pd
import uuid
from django.core.management.base import BaseCommand
from gymkhana.models import Venue
from users.models import CustomUser

class Command(BaseCommand):
    help = "Import venues from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']  # Read file path from arguments

        try:
            df = pd.read_excel(file_path)

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
                    department_incharge=incharge_user
                )
                venue.save()
                print(f"Created venue: {venue.venue_name}")

            print("Venue import completed successfully.")

        except Exception as e:
            print("Error importing venues:", e)
