from django.db import models

from employees.models import Employee


# Create your models here.
class Training(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название обучения")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

class TrainingRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    training = models.ForeignKey(Training, on_delete=models.CASCADE, verbose_name="Обучение")
    completion_date = models.DateField(verbose_name="Дата прохождения")
    is_completed = models.BooleanField(default=False, verbose_name="Пройдено")

    def __str__(self):
        return f"{self.employee} - {self.training}"