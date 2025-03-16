from datetime import datetime, timedelta
# Фильтр расходов за определенный месяц
def get_monthly_expenses(month, year):
    return Expense.objects.filter(date__year=year, date__month=month)

# Фильтр расходов за определенную неделю
def get_weekly_expenses(year, week_number):
    first_day_of_week = datetime.strptime(f'{year}-W{week_number}-1', "%Y-W%W-%w")
    last_day_of_week = first_day_of_week + timedelta(days=6)
    return Expense.objects.filter(date__range=[first_day_of_week, last_day_of_week])
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
        if self.share_type == 'percentage' and self.percentage is None:
            raise ValidationError("Если выбрано 'Процент', поле 'percentage' обязательно.")
        if self.share_type == 'fixed' and self.fixed_amount is None:
            raise ValidationError("Если выбрана 'Фиксированная сумма', поле 'fixed_amount' обязательно.")
        if self.share_type == 'percentage' and self.fixed_amount is not None:
            raise ValidationError("При выборе 'Процент' поле 'fixed_amount' должно быть пустым.")
        if self.share_type == 'fixed' and self.percentage is not None:
            raise ValidationError("При выборе 'Фиксированная сумма' поле 'percentage' должно быть пустым.")

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
    name = models.CharField(max_length=255)  # Название расхода
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )  # Сумма расхода
    date = models.DateField()  # Дата расхода
    category = models.CharField(max_length=100, choices=[
        ('rent', 'Аренда'),
        ('salary', 'Зарплата'),
        ('supplies', 'Закупки'),
        ('other', 'Другое'),
    ])  # Категория расхода
    description = models.TextField(blank=True, null=True)  # Описание

    def __str__(self):
        return f"{self.name} - {self.amount} KGS ({self.date})"
