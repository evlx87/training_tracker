import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from employees.models import TrainingRecord, Employee, TrainingProgram

logger = logging.getLogger('employees')


@receiver([post_save, post_delete], sender=TrainingRecord)
@receiver([post_save, post_delete], sender=Employee)
@receiver([post_save, post_delete], sender=TrainingProgram)
def invalidate_training_report_cache(sender, instance, **kwargs):
    try:
        cache.delete('training_report')
        logger.debug(
            'Кэш отчета по обучению очищен из-за изменения данных, модель: %s, экземпляр: %s',
            sender.__name__,
            instance)
    except Exception as e:
        logger.error(
            'Ошибка при очистке кэша отчета по обучению, модель: %s, ошибка: %s',
            sender.__name__,
            str(e),
            exc_info=True)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    try:
        post_data = request.POST.copy()
        post_data.pop('password', None)
        logger.info(
            'Пользователь %s вошел в систему, путь: %s, метод: %s, параметры: %s',
            user.username,
            request.path,
            request.method,
            post_data)
    except Exception as e:
        logger.error(
            'Ошибка при логировании входа пользователя %s: %s',
            user.username, str(e), exc_info=True
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    try:
        logger.info(
            'Пользователь %s вышел из системы, путь: %s, метод: %s',
            user.username, request.path, request.method
        )
    except Exception as e:
        logger.error(
            'Ошибка при логировании выхода пользователя %s: %s',
            user.username, str(e), exc_info=True
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    try:
        post_data = request.POST.copy()
        post_data.pop('password', None)
        username = credentials.get('username', 'Anonymous')
        logger.warning(
            'Неуспешная попытка входа, пользователь: %s, путь: %s, метод: %s, параметры: %s',
            username,
            request.path,
            request.method,
            post_data)
    except Exception as e:
        logger.error(
            'Ошибка при логировании неуспешной попытки входа пользователя %s: %s',
            username,
            str(e),
            exc_info=True)
