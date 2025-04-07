from rest_framework import serializers
from .models import Worker, Service, Client, Expense, Cabinets
from datetime import datetime


def is_string(value):
    return isinstance(value, str)


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class CabinetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinets
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


def is_string(value):
    return isinstance(value, str)


class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='full_name')
    phone = serializers.CharField(source='phone_number')
    date = serializers.CharField(write_only=True)

    master = serializers.JSONField()
    cabinet = serializers.JSONField()
    services = serializers.JSONField()
    product = serializers.JSONField()
    payment = serializers.CharField()

    # Добавляем эти поля для отображения
    appointment_date = serializers.DateField(read_only=True)
    appointment_time = serializers.TimeField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'name', 'phone', 'date', 'time',
            'appointment_date', 'appointment_time',
            'master', 'cabinet',
            'services', 'product',
            'payment'
        ]

    def create(self, validated_data):
        # Извлекаем и парсим дату
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

        # Извлекаем и парсим время
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

    def update(self, instance, validated_data):
        # Обработка даты
        date_str = validated_data.pop('date', None)
        if date_str:
            try:
                if '.' in date_str:
                    appointment_date = datetime.strptime(date_str, "%d.%m.%y").date()
                else:
                    appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                instance.appointment_date = appointment_date
            except (ValueError, TypeError):
                raise serializers.ValidationError({"date": "Неверный формат даты. Используй ДД.ММ.ГГ или ГГГГ-ММ-ДД."})

        # Обработка времени
        master_data = validated_data.get('master', {})
        time_str = master_data.get('time', None)
        if time_str:
            try:
                instance.appointment_time = datetime.strptime(time_str, "%H:%M").time()
            except (ValueError, TypeError):
                raise serializers.ValidationError({"master.time": "Неверный формат времени. Ожидается ЧЧ:ММ."})

        # Остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


# Сериализатор для статистики расходов
class DailyExpenseStatsSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    added_today = serializers.IntegerField()
    spent_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    items_spent_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
