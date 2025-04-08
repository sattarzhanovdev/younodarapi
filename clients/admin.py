from django.contrib import admin
from .models import Client, Service, Worker, WorkerServiceShare, WorkerServiceShareDetail, Expense, Cabinets, Stock

class WorkerServiceShareDetailInline(admin.TabularInline):  # Позволяет добавлять услуги на одной странице
    model = WorkerServiceShareDetail
    extra = 1  # Показывать 1 пустую строку для добавления новой услуги

class WorkerServiceShareAdmin(admin.ModelAdmin):
    list_display = ('worker',)
    inlines = [WorkerServiceShareDetailInline]  # Подключаем inline

admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Worker)
admin.site.register(Cabinets)
admin.site.register(Stock)
admin.site.register(WorkerServiceShare, WorkerServiceShareAdmin)
@admin.register(Expense)

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'price', 'quantity', 'unit')
    search_fields = ('name',)
