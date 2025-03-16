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
    services = ServiceSerializer(many=True, read_only=True)
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)  # Читаемый формат категории

    class Meta:
        model = Expense
        fields = '__all__'
