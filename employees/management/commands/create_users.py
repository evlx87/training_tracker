import logging

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

logger = logging.getLogger('employees')


class Command(BaseCommand):
    help = 'Создает пользователей ok, oob и mto с указанными группами'

    def handle(self, *args, **kwargs):
        # Создание или получение групп
        editors_group, _ = Group.objects.get_or_create(name='Editors')
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')

        # Данные пользователей
        users_data = [
            {'username': 'ok', 'password': 'password123', 'group': editors_group},
            {'username': 'oob', 'password': 'password456', 'group': editors_group},
            {'username': 'mto', 'password': 'password789', 'group': moderators_group},
        ]

        for user_data in users_data:
            username = user_data['username']
            password = user_data['password']
            group = user_data['group']

            # Создание или получение пользователя
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'is_active': True,
                }
            )

            if created:
                user.set_password(password)
                user.save()
                logger.info(f"Создан пользователь: {username}")
            else:
                logger.info(f"Пользователь {username} уже существует")

            # Назначение группы
            user.groups.add(group)
            logger.info(
                f"Пользователь {username} добавлен в группу {
                    group.name}")

        logger.info('Создание пользователей завершено!')
