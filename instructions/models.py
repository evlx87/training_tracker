from django.db import models


class Instruction(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
        db_index=True
    )
    content = models.TextField(
        verbose_name='Содержание'
    )
    category = models.CharField(
        max_length=100,
        verbose_name='Категория',
        default='Общее'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Инструкция'
        verbose_name_plural = 'Инструкции'
        ordering = ['category', 'title']
