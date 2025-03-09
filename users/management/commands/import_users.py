import pandas as pd
import uuid
from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = "Import users from an Excel file"
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']  # Read file path from arguments
        
        try:
            df = pd.read_excel(file_path)

            for index, row in df.iterrows():
                if CustomUser.objects.filter(email=row['email']).exists():
                    print(f"User {row['email']} already exists. Skipping...")
                    continue

                user = CustomUser(
                    id=uuid.uuid4(),
                    name=row['name'],
                    email=row['email'],
                    organization_name=row.get('organization_name', ''),
                    organization_type=row.get('organization_type', ''),
                    role=row['role'],
                    password=row['password'],  # Hash the password in production
                )
                user.set_password(row['password'])  # Hash password
                user.save()
                print(f"Created user: {user.email}")

            print("User import completed successfully.")

        except Exception as e:
            print("Error importing users:", e)
