from rest_framework import serializers
from .models import Client, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price']

class ClientSerializer(serializers.ModelSerializer):
    service_type = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'full_name', 'phone_number', 'total_price', 'service_type']
