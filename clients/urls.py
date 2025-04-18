from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, ServiceViewSet, ClientViewSet, ExpenseListCreateView, ExpenseDetailView, MonthlyExpensesView, ExpenseStatsView, ClientsAddedTodayView, CabinetsViewSet, StockViewSet, BusinessStatsView, StaffProfitView, CashDailyStatsView

router = DefaultRouter()
router.register(r'workers', WorkerViewSet)
router.register(r'cabinets', CabinetsViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'stock', StockViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/monthly/<int:year>/<int:month>/', MonthlyExpensesView.as_view(), name='monthly-expenses'),
    path('expenses/stats/daily/', ExpenseStatsView.as_view(), name='daily-expense-stats'),
    path('today/', ClientsAddedTodayView.as_view(), name='clients-today'),
    path('stats/monthly/', BusinessStatsView.as_view(), name='monthly-stats'),
    path('stats/staff/', StaffProfitView.as_view()),
    path('stats/cash-daily/', CashDailyStatsView.as_view(), name='cash-daily-stats'),

]
