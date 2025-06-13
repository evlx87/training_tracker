from django.db import models


class TrainingProgram(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    duration_days = models.PositiveIntegerField(
        verbose_name='Длительность (дней)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Программа обучения'
        verbose_name_plural = 'Программы обучения'

    def __str__(self):
        return self.name
