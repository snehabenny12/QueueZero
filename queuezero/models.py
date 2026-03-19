from django.db import models
from hospital.models import Patient, Doctor
from django.contrib.auth.models import User  

class Token(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('served', 'Served'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='queuezero_tokens')
    token_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    is_called = models.BooleanField(default=False)  # For backward compatibility
    pre_alert_sent = models.BooleanField(default=False)  # Track if alert was already sent
    # QR Code field
    qr_image = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        unique_together = ['doctor', 'token_number']
    
    def __str__(self):
        return f"Token {self.token_number} - {self.patient.user.username}"

    @property
    def patients_ahead(self):
        return Token.objects.filter(
            doctor=self.doctor,
            status='waiting',
            created_at__lt=self.created_at
        ).count()

    @property
    def estimated_wait_time(self):
        # Calculate based on doctor's average slot time
        avg_time = getattr(self.doctor, 'avg_slot_minutes', 10)
        return self.patients_ahead * avg_time
def home(request):
    return render(request, "hospital/home.html")
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # fixed fee
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} - {'Success' if self.is_successful else 'Failed'}"
