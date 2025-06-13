import logging

from django.db import models

from departments.models import Department
from positions.models import Position
from trainings.models import TrainingProgram

logger = logging.getLogger('employees')


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
