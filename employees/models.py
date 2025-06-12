import logging
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse

logger = logging.getLogger('employees')


class Department(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Position(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Employee(models.Model):
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
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
        verbose_name='Должность')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Подразделение')
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата трудоустройства')
    is_dismissed = models.BooleanField(default=False, verbose_name='Уволен')
    dismissal_date = models.DateField(
        null=True, blank=True, verbose_name='Дата увольнения')
    is_on_maternity_leave = models.BooleanField(
        default=False, verbose_name='В декрете')
    is_external_part_time = models.BooleanField(
        default=False, verbose_name='Внешний совместитель')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        unique_together = ['last_name', 'first_name', 'middle_name']


class TrainingProgram(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название')
    recurrence_period = models.IntegerField(
        null=True, blank=True, verbose_name='Периодичность (годы)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Программа обучения'
        verbose_name_plural = 'Программы обучения'


class TrainingRecord(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник')
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        verbose_name='Программа обучения')
    completion_date = models.DateField(verbose_name='Дата прохождения')
    details = models.TextField(blank=True, verbose_name='Детали')

    def __str__(self):
        return f'{self.employee} - {self.training_program} ({self.completion_date})'

    def is_overdue(self):
        if not self.training_program.recurrence_period:
            return False
        from datetime import date, timedelta
        expiry_date = self.completion_date + \
            timedelta(days=self.training_program.recurrence_period * 365)
        return date.today() > expiry_date

    class Meta:
        verbose_name = 'Запись об обучении'
        verbose_name_plural = 'Записи об обучении'
        unique_together = ['employee', 'training_program', 'completion_date']


class DeletionRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_APPROVED, 'Подтверждено'),
        (STATUS_REJECTED, 'Отклонено'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deletion_requests')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус')
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_deletion_requests',
        verbose_name='Рассмотрел')
    reviewed_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Дата рассмотрения')

    def __str__(self):
        return f"Запрос на удаление {self.content_object} от {self.created_by} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Запрос на удаление'
        verbose_name_plural = 'Запросы на удаление'
