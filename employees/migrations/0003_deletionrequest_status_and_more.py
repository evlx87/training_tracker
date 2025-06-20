# Generated by Django 5.2.3 on 2025-06-15 15:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('employees', '0002_alter_employee_unique_together_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='deletionrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')], default='pending', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Тип объекта'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deletion_requests', to=settings.AUTH_USER_MODEL, verbose_name='Автор запроса'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='object_id',
            field=models.PositiveIntegerField(verbose_name='ID объекта'),
        ),
    ]
