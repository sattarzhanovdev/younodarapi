from django.contrib import admin
from .models import Service, Worker, WorkerServiceShare, WorkerServiceShareDetail

class WorkerServiceShareDetailInline(admin.TabularInline):  # Позволяет добавлять услуги на одной странице
    model = WorkerServiceShareDetail
    extra = 1  # Показывать 1 пустую строку для добавления новой услуги

class WorkerServiceShareAdmin(admin.ModelAdmin):
    list_display = ('worker',)
    inlines = [WorkerServiceShareDetailInline]  # Подключаем inline

admin.site.register(Service)
admin.site.register(Worker)
admin.site.register(WorkerServiceShare, WorkerServiceShareAdmin)
