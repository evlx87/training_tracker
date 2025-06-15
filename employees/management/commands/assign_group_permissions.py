import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from employees.models import Employee, Department, Position, TrainingProgram, TrainingRecord

logger = logging.getLogger('employees')


class Command(BaseCommand):
    help = 'Назначает права доступа группам Editors и Moderators'

    def handle(self, *args, **kwargs):
        editors_group, _ = Group.objects.get_or_create(name='Editors')
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        models = [
            Employee,
            Department,
            Position,
            TrainingProgram,
            TrainingRecord]
        content_types = {model.__name__.lower(): ContentType.objects.get_for_model(
            model) for model in models}
        editor_permissions = ['add_{model}', 'change_{model}']
        moderator_permissions = [
            'add_{model}',
            'change_{model}',
            'delete_{model}']
        for model_name in content_types.keys():
            for perm in editor_permissions:
                permission_codename = perm.format(model=model_name)
                try:
                    permission = Permission.objects.get(
                        content_type=content_types[model_name],
                        codename=permission_codename
                    )
                    editors_group.permissions.add(permission)
                    logger.info(
                        f"Добавлено право '{permission_codename}' для группы Editors")
                except Permission.DoesNotExist:
                    logger.warning(
                        f"Право '{permission_codename}' не найдено для модели {model_name}")
        for model_name in content_types.keys():
            for perm in moderator_permissions:
                permission_codename = perm.format(model=model_name)
                try:
                    permission = Permission.objects.get(
                        content_type=content_types[model_name],
                        codename=permission_codename
                    )
                    moderators_group.permissions.add(permission)
                    logger.info(
                        f"Добавлено право '{permission_codename}' для группы Moderators")
                except Permission.DoesNotExist:
                    logger.warning(
                        f"Право '{permission_codename}' не найдено для модели {model_name}")
        logger.info('Назначение прав группам завершено!')
