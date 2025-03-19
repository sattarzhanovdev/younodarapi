from rest_framework import viewsets, generics
from django.utils.timezone import now
from django.db.models import Sum
from .models import Worker, Service, Client, Expense
from .serializers import WorkerSerializer, ServiceSerializer, ClientSerializer, ExpenseSerializer
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
class DailyExpenseStatsView(APIView):
    def get(self, request):
        today = now().date()

        total_items = Expense.objects.count()  # Общее количество наименований
        added_today = Expense.objects.filter(date=today).count()  # Добавлено сегодня
        spent_today = Expense.objects.filter(date=today).aggregate(total_spent=Sum('amount'))['total_spent'] or 0  # Израсходовано за сегодня

        return Response({
            "total_items": total_items,
            "added_today": added_today,
            "spent_today": spent_today
        })
