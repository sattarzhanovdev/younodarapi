from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import now

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
    full_name = models.CharField(max_length=255)
    appointment_day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    appointment_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    appointment_time = models.TimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    services = models.ManyToManyField(Service)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)

    def __str__(self):
        time_str = self.appointment_time.strftime('%H:%M') if self.appointment_time else "Без времени"
        return f"{self.full_name} — {self.appointment_day}/{self.appointment_month} {time_str}"

class Expense(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    date = models.DateField()
    category = models.CharField(max_length=100, choices=[
        ('rent', 'Аренда'),
        ('salary', 'Зарплата'),
        ('supplies', 'Закупки'),
        ('other', 'Другое'),
    ])
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.amount} KGS ({self.date})"

    @property
    def day_expense(self):
        return Expense.objects.filter(date=self.date).aggregate(total=models.Sum('amount'))['total'] or 0

# Фильтр расходов за определенный месяц
def get_monthly_expenses(month=None, year=None):
    today = now().date()
    month = month or today.month
    year = year or today.year
    return Expense.objects.filter(date__year=year, date__month=month)

# Фильтр расходов за определенную неделю
def get_weekly_expenses(year, week_number):
    first_day_of_week = datetime.fromisocalendar(year, week_number, 1).date()
    last_day_of_week = first_day_of_week + timedelta(days=6)
    return Expense.objects.filter(date__range=[first_day_of_week, last_day_of_week])
