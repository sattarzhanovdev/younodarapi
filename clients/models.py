from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class Worker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Cabinets(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plusToday = models.DecimalField(max_digits=10, decimal_places=2)
    minusToday = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name



class WorkerServiceShare(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    service = models.ManyToManyField(Service, through='WorkerServiceShareDetail')

    def __str__(self):
        return f"{self.worker}"


class WorkerServiceShareDetail(models.Model):
    worker_service_share = models.ForeignKey(WorkerServiceShare, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    share_type = models.CharField(
        max_length=10,
        choices=[('percentage', 'Процент'), ('fixed', 'Фиксированная сумма')],
        default='percentage'
    )
    percentage = models.FloatField(null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def clean(self):
        if self.share_type == 'percentage':
            if self.percentage is None or self.fixed_amount is not None:
                raise ValidationError("При выборе 'Процент' заполните 'percentage' и оставьте 'fixed_amount' пустым.")
        elif self.share_type == 'fixed':
            if self.fixed_amount is None or self.percentage is not None:
                raise ValidationError("При выборе 'Фиксированная сумма' заполните 'fixed_amount' и оставьте 'percentage' пустым.")

    def __str__(self):
        return f"{self.worker_service_share.worker} - {self.service} ({self.share_type})"


class Client(models.Model):
    id=models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    services = models.JSONField(null=True, blank=True)
    product = models.JSONField(null=True, blank=True)
    master = models.JSONField(null=True, blank=True)
    cabinet = models.JSONField(null=True, blank=True)
    payment = models.CharField(max_length=50)
    time = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.full_name} — {self.appointment_date} {self.appointment_time}"

    @property
    def total_cost(self):
        total = 0
        for service in self.services or []:
            total += float(service.get("price", 0))
        for item in self.product or []:
            total += float(item.get("price", 0)) * int(item.get("amount", 1))
        return total


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=50)

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.amount} ({self.unit})"


# Вспомогательные функции

def get_monthly_expenses(month=None, year=None):
    today = now().date()
    month = month or today.month
    year = year or today.year
    return Expense.objects.filter(date__year=year, date__month=month)


def get_weekly_expenses(year, week_number):
    first_day_of_week = datetime.fromisocalendar(year, week_number, 1).date()
    last_day_of_week = first_day_of_week + timedelta(days=6)
    return Expense.objects.filter(date__range=[first_day_of_week, last_day_of_week])
