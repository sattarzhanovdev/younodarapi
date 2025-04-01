from rest_framework import serializers
from .models import Worker, Service, Client, Expense

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer()  # Вложенный сериализатор для работника
    services = ServiceSerializer(many=True)  # Вложенный сериализатор для списка услуг

    class Meta:
        model = Client
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# Сериализатор для статистики расходов
class DailyExpenseStatsSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    added_today = serializers.IntegerField()
    spent_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    items_spent_today = serializers.IntegerField()  # Количество товаров, которые были израсходованы сегодня
