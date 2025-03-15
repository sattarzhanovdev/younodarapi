from django.contrib import admin
from .models import Client, Service, Worker

admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Worker)
