from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, ServiceViewSet, ClientViewSet, ExpenseListCreateView, ExpenseDetailView, MonthlyExpensesView

router = DefaultRouter()
router.register(r'workers', WorkerViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/monthly/<int:year>/<int:month>/', MonthlyExpensesView.as_view(), name='monthly-expenses'),
]
