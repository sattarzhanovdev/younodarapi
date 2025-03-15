# Generated by Django 5.1.7 on 2025-03-15 18:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_client_appointment_time_alter_client_appointment_day_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerServiceShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_type', models.CharField(choices=[('percentage', 'Процент'), ('fixed', 'Фиксированная сумма')], default='percentage', max_length=10)),
                ('percentage', models.FloatField(blank=True, null=True)),
                ('fixed_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.service')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.worker')),
            ],
        ),
    ]
