import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Worker(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Client(models.Model):
    full_name = models.CharField(max_length=255)
    appointment_day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    appointment_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    appointment_time = models.TimeField(default="12:00")
    phone_number = models.CharField(max_length=20)
    services = models.ManyToManyField("Service")
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.full_name} — {self.appointment_day}/{self.appointment_month} {self.appointment_time.strftime('%H:%M')}"
