from rest_framework import serializers
from .models import Worker, Service, Client, Expense
from datetime import datetime

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='full_name')
    phone = serializers.CharField(source='phone_number')
    date = serializers.CharField(write_only=True)

    master = serializers.JSONField()
    cabinet = serializers.JSONField()
    services = serializers.JSONField()
    product = serializers.JSONField()
    payment = serializers.CharField()

    class Meta:
        model = Client
        fields = ['name', 'phone', 'date', 'master', 'cabinet', 'services', 'product', 'payment']

    def create(self, validated_data):
        # Извлекаем и преобразуем данные
        date_str = validated_data.pop('date')  # "22.05.25"
        appointment_date = datetime.strptime(date_str, "%d.%m.%y").date()

        master_data = validated_data.get('master', {})
        appointment_time = master_data.get('time', '00:00')

        # Добавляем нужные поля для модели
        validated_data['appointment_date'] = appointment_date
        validated_data['appointment_time'] = appointment_time

        return Client.objects.create(**validated_data)
      

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
