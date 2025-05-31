import logging

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from employees.models import TrainingRecord, Employee, TrainingProgram

logger = logging.getLogger('employees')


@receiver([post_save, post_delete], sender=TrainingRecord)
@receiver([post_save, post_delete], sender=Employee)
@receiver([post_save, post_delete], sender=TrainingProgram)
def invalidate_training_report_cache(sender, instance, **kwargs):
    cache.delete('training_report')
    logger.debug('Кэш отчета по обучению очищен из-за изменения данных')
