from rest_framework import viewsets, generics
from django.utils.timezone import now
from django.db.models import Sum
from .models import Worker, Service, Client, Expense
from .serializers import WorkerSerializer, ServiceSerializer, ClientSerializer, ExpenseSerializer, DailyExpenseStatsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

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
