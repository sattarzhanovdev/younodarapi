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
      fields = [
          'name', 'phone', 'date',
          'master', 'cabinet',
          'services', 'product',
          'payment'
      ]

    def create(self, validated_data):
        date_str = validated_data.pop('date', None)

        if not is_string(date_str):
            raise serializers.ValidationError({"date": "Дата должна быть строкой, например '22.05.25' или '2025-04-04'"})

        try:
          if '.' in date_str:
              appointment_date = datetime.strptime(date_str, "%d.%m.%y").date()
          else:
              appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
          raise serializers.ValidationError({"date": "Неверный формат даты. Используй ДД.ММ.ГГ или ГГГГ-ММ-ДД."})


        master_data = validated_data.get('master', {})
        time_str = master_data.get('time', '00:00')

        if not is_string(time_str):
            raise serializers.ValidationError({"master.time": "Время должно быть строкой в формате ЧЧ:ММ"})

        try:
            appointment_time = datetime.strptime(time_str, "%H:%M").time()
        except (ValueError, TypeError):
            raise serializers.ValidationError({"master.time": "Неверный формат времени. Ожидается ЧЧ:ММ."})

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
