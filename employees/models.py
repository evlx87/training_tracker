from django.db import models


# Create your models here.
class Department(models.Model):
    """Модель для структурных подразделений организации"""
    name = models.CharField(max_length=100, verbose_name="Название подразделения")
    description = models.TextField(blank=True, verbose_name="Описание", null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

class Position(models.Model):
    """Модель для должностей"""
    name = models.CharField(max_length=100, verbose_name="Название должности")
    description = models.TextField(blank=True, verbose_name="Описание", null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

class Employee(models.Model):
    """Модель для сотрудников"""
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество", blank=True)
    birth_date = models.DateField(verbose_name="Дата рождения")  # Формат ДД.ММ.ГГГГ задается в формах/шаблонах
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, verbose_name="Должность")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Подразделение")
    is_dismissed = models.BooleanField(default=False, verbose_name="Уволен")
    dismissal_date = models.DateField(blank=True, null=True, verbose_name="Дата увольнения")
    is_on_maternity_leave = models.BooleanField(default=False, verbose_name="В декрете")

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"