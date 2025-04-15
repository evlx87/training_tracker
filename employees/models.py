from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название подразделения")
    description = models.TextField(blank=True, verbose_name="Описание", null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"


class Position(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название должности")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class Employee(models.Model):
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество", blank=True)
    birth_date = models.DateField(verbose_name="Дата рождения")
    position = models.ForeignKey('employees.Position', on_delete=models.SET_NULL, null=True, verbose_name="Должность")
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, null=True,
                                   verbose_name="Подразделение")
    is_dismissed = models.BooleanField(default=False, verbose_name="Уволен")
    dismissal_date = models.DateField(blank=True, null=True, verbose_name="Дата увольнения")
    is_on_maternity_leave = models.BooleanField(default=False, verbose_name="В декрете")
    is_external_part_time = models.BooleanField(default=False, verbose_name="Внешний совместитель")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
