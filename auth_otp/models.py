from django.db import models
from django.utils import timezone

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)
    
    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email} ({'verified' if self.is_verified else 'pending'})"