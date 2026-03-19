from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient")
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    DEPARTMENT_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        # Add more departments as needed
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor")
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    is_available = models.BooleanField(default=True)
    avg_slot_minutes = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='hospital_tokens')
    status = models.CharField(max_length=20, default="Waiting")
    created_at = models.DateTimeField(auto_now_add=True)
    qr_image = models.ImageField(upload_to="tokens/", null=True, blank=True)

def __str__(self):
    return f"Token for {self.user.username} with {self.doctor}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name