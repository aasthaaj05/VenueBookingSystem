import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Custom User Manager (Without Superuser)
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

# Custom User Model (Without Superuser)
class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = [
        ('club', 'Club'),
        ('fests', 'Fests'),
        ('student_chapter', 'Student Chapter'),
        ('faculty', 'Faculty'),
        ('HOD', 'HOD'),
        ('Dean', 'Dean'),
        ('VC', 'VC'),
        ('Registrar', 'Registrar'),
        ('outsider', 'Outsider'),
        ('gymkhana', 'Gymkhana'),
        ('faculty_advisor', 'Faculty_advisor'),
        ('venue_admin', 'Venue_admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    organization_type = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='outsider')
    password = models.CharField(max_length=255)  # Password is hashed internally

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()  # Custom manager for handling user creation

    USERNAME_FIELD = 'email'  # Users log in using email
    REQUIRED_FIELDS = ['name']  # Name is required

    def __str__(self):
        return self.email

