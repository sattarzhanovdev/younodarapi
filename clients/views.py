from rest_framework import viewsets, generics, status
from django.utils.timezone import now
from django.db.models import Sum
from .models import Worker, Service, Client, Expense
from .serializers import WorkerSerializer, ServiceSerializer, ClientSerializer, ExpenseSerializer, DailyExpenseStatsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime


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


class DailyStatsView(APIView):
    def get(self, request, *args, **kwargs):
        today = now().date()

        clients_today = Client.objects.filter(appointment_date=today).count()
        spent_today = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
        items_spent_today = Expense.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0

        data = {
            "total_items": Expense.objects.count(),
            "added_today": clients_today,
            "spent_today": spent_today,
            "items_spent_today": items_spent_today
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
