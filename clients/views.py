from rest_framework import viewsets, generics
from django.utils.timezone import now
from django.db.models import Sum
from .models import Worker, Service, Client, Expense
from .serializers import WorkerSerializer, ServiceSerializer, ClientSerializer, ExpenseSerializer, DailyExpenseStatsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_time
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend



class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['appointment_day', 'appointment_month', 'worker']

class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class MonthlyExpensesView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        month = self.kwargs['month']
        year = self.kwargs.get('year', now().year)
        return Expense.objects.filter(date__year=year, date__month=month)

# Новое представление для статистики по расходам

class DailyStatsView(APIView):
    def get(self, request, *args, **kwargs):
        today = now().date()

        # Подсчет клиентов, добавленных сегодня
        clients_today = Client.objects.filter(appointment_day=today.day, appointment_month=today.month).count()

        # Подсчет суммы расходов за сегодня
        spent_today = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0

        # Подсчет количества израсходованных товаров за сегодня
        items_spent_today = Expense.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0

        data = {
            "total_items": Expense.objects.count(),
            "added_today": clients_today,
            "spent_today": spent_today,
            "items_spent_today": items_spent_today  # Новое поле
        }

        serializer = DailyExpenseStatsSerializer(data)
        return Response(serializer.data)


class ClientsAddedTodayView(APIView):
    def get(self, request):
        today = now().date()
        count = Client.objects.filter(appointment_day=today.day, appointment_month=today.month).count()
        return Response({"clients_added_today": count})







# POST

from rest_framework import serializers
from .models import Client
from datetime import datetime

class ClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='full_name')
    phone = serializers.CharField(source='phone_number')
    date = serializers.CharField(write_only=True)  # "22.05.25"

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
        date_str = validated_data.pop('date')
        appointment_date = datetime.strptime(date_str, "%d.%m.%y").date()
        appointment_time = validated_data['master'].get('time', '00:00')
        validated_data['appointment_date'] = appointment_date
        validated_data['appointment_time'] = appointment_time
        return Client.objects.create(**validated_data)

    def update(self, instance, validated_data):
        date_str = validated_data.pop('date', None)
        if date_str:
            appointment_date = datetime.strptime(date_str, "%d.%m.%y").date()
            instance.appointment_date = appointment_date

        if 'master' in validated_data:
            instance.appointment_time = validated_data['master'].get('time', instance.appointment_time)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
