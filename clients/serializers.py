from rest_framework import serializers
from .models import Worker, Service, Client

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
