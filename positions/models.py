from django.db import models


class Position(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
        db_index=True)
    is_manager = models.BooleanField(
        default=False,
        verbose_name='Руководитель',
        db_index=True)
    is_teacher = models.BooleanField(
        default=False,
        verbose_name='Педагогический работник',
        db_index=True)

    def __str__(
            self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
