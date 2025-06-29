# Generated by Django 5.2.3 on 2025-06-15 15:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_deletionrequest_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='deletionrequest',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата обработки'),
        ),
        migrations.AddField(
            model_name='deletionrequest',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_deletion_requests', to=settings.AUTH_USER_MODEL, verbose_name='Обработал'),
        ),
    ]
