from rest_framework import viewsets, generics, status
from django.utils.timezone import now
from django.db.models import Sum, F
from .models import Worker, Service, Client, Expense, Cabinets, Stock
from .serializers import WorkerSerializer, ServiceSerializer, ClientSerializer, ExpenseSerializer, StockSerializer,DailyExpenseStatsSerializer, CabinetsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.utils import timezone
from datetime import date, timedelta
from django.db import models
from django.db.models import DecimalField
from decimal import Decimal
from collections import defaultdict
from calendar import monthrange
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')



class BusinessStatsView(APIView):
    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)

        # --- МЕСЯЦ ---
        monthly_expense = Expense.objects.filter(
            date__gte=first_day
        ).aggregate(
            total=Sum(F('quantity') * F('price'), output_field=DecimalField())
        )['total'] or Decimal("0.00")

        paid_clients_month = Client.objects.filter(
            appointment_date__gte=first_day
        )
        monthly_revenue = sum([c.total_cost for c in paid_clients_month], Decimal("0.00"))
        monthly_clients = paid_clients_month.count()
        monthly_profit = monthly_revenue - monthly_expense

        # --- ДЕНЬ ---
        daily_expense = Expense.objects.filter(
            date=today
        ).aggregate(
            total=Sum(F('quantity') * F('price'), output_field=DecimalField())
        )['total'] or Decimal("0.00")

        paid_clients_day = Client.objects.filter(
            appointment_date=today
        )
        daily_revenue = sum([c.total_cost for c in paid_clients_day], Decimal("0.00"))
        daily_clients = paid_clients_day.count()
        daily_profit = daily_revenue - daily_expense

        return Response({
            # Месяц
            'monthly_expense': monthly_expense,
            'monthly_revenue': monthly_revenue,
            'monthly_profit': monthly_profit,
            'monthly_clients': monthly_clients,

            # День
            'daily_expense': daily_expense,
            'daily_revenue': daily_revenue,
            'daily_profit': daily_profit,
            'daily_clients': daily_clients,
        }, status=status.HTTP_200_OK)
        

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Если отправлен список
        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CabinetsViewSet(viewsets.ModelViewSet):
    queryset = Cabinets.objects.all()
    serializer_class = CabinetsSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend]


class ExpenseListCreateView(APIView):
    def get(self, request):
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверяем: это массив?
        if isinstance(request.data, list):
            serializer = ExpenseSerializer(data=request.data, many=True)
        else:
            serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(APIView):
    def get_object(self, pk):
        try:
            return Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
            return None

    def get(self, request, pk):
        expense = self.get_object(pk)
        if not expense:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    def put(self, request, pk):
        expense = self.get_object(pk)
        if not expense:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk)
        if not expense:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class MonthlyExpensesView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        month = self.kwargs['month']
        year = self.kwargs.get('year', now().year)
        return Expense.objects.filter(date__year=year, date__month=month)


class ExpenseStatsView(APIView):
    def get(self, request):
        today = date.today()

        # Получаем начало и конец текущего месяца
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=28) + timezone.timedelta(days=4)  # это даст нам следующий месяц, отнимем 1 день
        last_day_of_month = last_day_of_month.replace(day=1) - timezone.timedelta(days=1)

        # Статистика для всего времени
        total_items = Expense.objects.count()
        added_today = Expense.objects.filter(date=today).count()

        # Статистика за сегодня
        spent_today = Expense.objects.filter(date=today).aggregate(
            total=Sum('price')  # Сумма потраченных средств за сегодня (quantity)
        )['total'] or 0

        items_spent_today = Expense.objects.filter(date=today).aggregate(
            total=Sum('amount')  # Сумма потраченных единиц за сегодня (amount)
        )['total'] or 0

        # Статистика за месяц
        income_this_month = Expense.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).aggregate(
            total=Sum('quantity')  # Доход (по quantity) за месяц
        )['total'] or 0

        expense_this_month = Expense.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).aggregate(
            total=Sum('price')  # Расход (по amount) за месяц
        )['total'] or 0

        # Подготовка данных
        data = {
            'total_items': total_items,
            'added_today': added_today,
            'spent_today': spent_today,
            'items_spent_today': items_spent_today,
            'income_this_month': income_this_month,
            'expense_this_month': expense_this_month
        }

        serializer = DailyExpenseStatsSerializer(data)
        return Response(serializer.data)


class ClientsAddedTodayView(APIView):
    def get(self, request):
        today = now().date()
        count = Client.objects.filter(appointment_date=today).count()
        return Response({"clients_added_today": count})


class ClientDetailView(APIView):
    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return None

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffProfitView(APIView):
    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)

        # Только оплаченные клиенты за текущий месяц
        clients = Client.objects.filter(
            appointment_date__gte=first_day,
            payment='full'
        )

        stats = defaultdict(lambda: {
            'revenue': Decimal('0.00'),
            'profit': Decimal('0.00'),
            'balance': Decimal('0.00'),
            'count': 0
        })

        for client in clients:
            services = client.services or []
            for service in services:
                master_name = service.get('assigned', 'Не указан')
                price = Decimal(service.get('price', 0))

                stats[master_name]['revenue'] += price
                stats[master_name]['profit'] += price * Decimal('0.30')  # можно поменять %
                stats[master_name]['balance'] += price
                stats[master_name]['count'] += 1

        result = []
        for i, (master, data) in enumerate(stats.items(), 1):
            result.append({
                'id': i,
                'name': master,
                'revenue': f"{data['revenue']:.2f}",
                'profit': f"{data['profit']:.2f}",
                'balance': f"{data['balance']:.2f}",
                'count': data['count']
            })

        return Response(result, status=status.HTTP_200_OK)
    
    
class CashDailyStatsView(APIView):
    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today

        stats_by_day = defaultdict(lambda: {
            'revenue': Decimal('0.00'),
            'profit': Decimal('0.00'),
            'balance': Decimal('0.00'),
            'count': 0
        })

        clients = Client.objects.filter(
            appointment_date__gte=first_day,
            appointment_date__lte=last_day,
        )

        for client in clients:
            appointment_day = client.appointment_date
            services = client.services or []

            for service in services:
                price = Decimal(service.get('price', 0))
                stats_by_day[appointment_day]['revenue'] += price
                stats_by_day[appointment_day]['profit'] += price * Decimal('0.30')  # или другой %
                stats_by_day[appointment_day]['balance'] += price
                stats_by_day[appointment_day]['count'] += 1

        result = []
        for i, (day, data) in enumerate(sorted(stats_by_day.items()), 1):
            result.append({
                'id': i,
                'date': day.strftime('%-d %B'),  # Например: "12 марта"
                'revenue': f"{data['revenue']:.2f}",
                'profit': f"{data['profit']:.2f}",
                'balance': f"{data['balance']:.2f}",
                'count': data['count']
            })

        return Response(result, status=status.HTTP_200_OK)