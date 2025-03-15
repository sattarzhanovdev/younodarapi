from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=255)  # Название услуги
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=255)  # ФИО сотрудника

    def __str__(self):
        return self.name
      
class Client(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания записи
    full_name = models.CharField(max_length=255)  # ФИО клиента
    phone_number = models.CharField(max_length=20)  # Номер телефона
    service_type = models.ManyToManyField(Service)  # Обновлено    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)  # Сотрудник
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Итоговая цена

    def __str__(self):
        return self.full_name
