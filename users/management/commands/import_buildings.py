import pandas as pd
import uuid
import os
from django.core.management.base import BaseCommand
from gymkhana.models import Building

class Command(BaseCommand):
    help = "Import buildings from a CSV or Excel file"

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
                'Building Name': 'name',
                'Total Floors': 'total_floors',
                'Building Location': 'location',
                'Pictures URL': 'photo_url',
                'Description': 'description'
            }, inplace=True)

            for index, row in df.iterrows():
                # Create and save building entry
                building, created = Building.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'location': row['location'],
                        'total_floors': row.get('total_floors'),
                        'photo_url': row.get('photo_url', ''),
                        'description': row.get('description', '')
                    }
                )

                if created:
                    print(f"Created building: {building.name}")
                else:
                    print(f"Building already exists: {building.name}")

            print("Building import completed successfully.")

        except Exception as e:
            print("Error importing buildings:", e)
