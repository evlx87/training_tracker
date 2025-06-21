from datetime import timedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from departments.models import Department
from positions.models import Position
from trainings.models import TrainingProgram


class Employee(models.Model):
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия',
        db_index=True)
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя')
    middle_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Отчество')
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения')
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Должность'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Подразделение'
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата трудоустройства')
    is_dismissed = models.BooleanField(
        default=False,
        verbose_name='Уволен')
    dismissal_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата увольнения')
    is_on_maternity_leave = models.BooleanField(
        default=False,
        verbose_name='В декрете')
    is_external_part_time = models.BooleanField(
        default=False,
        verbose_name='Внешний совместитель')
    is_safety_commission_member = models.BooleanField(
        default=False,
        verbose_name='Член комиссии по охране труда')

    def clean(self):
        if self.dismissal_date and not self.is_dismissed:
            raise ValidationError(
                'Дата увольнения указана, но сотрудник не помечен как уволенный.')
        if self.is_dismissed and not self.dismissal_date:
            raise ValidationError(
                'Сотрудник помечен как уволенный, но дата увольнения не указана.')
        super().clean()

    def __str__(self):
        middle_name = f' {self.middle_name}' if self.middle_name else ''
        return f'{self.last_name} {self.first_name}{middle_name}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        unique_together = (
            'last_name',
            'first_name',
            'middle_name',
            'birth_date')


class DeletionRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_APPROVED, 'Одобрено'),
        (STATUS_REJECTED, 'Отклонено'),
    )

    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        verbose_name='Тип объекта')
    object_id = models.PositiveIntegerField(verbose_name='ID объекта')
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deletion_requests',
        verbose_name='Автор запроса')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_deletion_requests',
        verbose_name='Обработал',
        blank=True)
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата обработки')

    def __str__(self):
        return f'Запрос на удаление {self.content_object} от {self.created_by} ({self.get_status_display()})'

    class Meta:
        verbose_name = 'Запрос на удаление'
        verbose_name_plural = 'Запросы на удаление'


class TrainingRecord(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник'
    )
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        verbose_name='Программа обучения'
    )
    completion_date = models.DateField(
        verbose_name='Дата прохождения'
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name='Детали'
    )
    document = models.FileField(
        upload_to='training_documents/',
        blank=True,
        null=True,
        verbose_name='Скан документа'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Подтверждено'
    )

    def __str__(self):
        return f"{self.employee} - {self.training_program} ({self.completion_date})"

    class Meta:
        verbose_name = 'Запись об обучении'
        verbose_name_plural = 'Записи об обучении'
        unique_together = ('employee', 'training_program', 'completion_date')