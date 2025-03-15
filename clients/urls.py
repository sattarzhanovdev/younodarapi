from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, ServiceViewSet, ClientViewSet

router = DefaultRouter()
router.register(r'workers', WorkerViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
