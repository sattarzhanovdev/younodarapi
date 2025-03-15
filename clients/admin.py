from django.contrib import admin
from .models import Client, Service

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'total_price')
    filter_horizontal = ('service_type',)  # Позволяет удобно выбирать услуги

admin.site.register(Service)  
