from django.db import models


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

