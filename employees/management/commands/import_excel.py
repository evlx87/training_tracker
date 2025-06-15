import logging
import os
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from employees.models import Employee, Department, Position, TrainingProgram, TrainingRecord

logger = logging.getLogger('employees')


class Command(BaseCommand):
    help = 'Импортирует данные из Excel файла в базу данных'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(
            settings.BASE_DIR,
            'data_upload',
            'обучение.xlsx')
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return
        try:
            df = pd.read_excel(file_path, header=[0, 1, 2], engine='openpyxl')
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {e}")
            return
        logger.info(f"Заголовки столбцов: {df.columns.tolist()}")
        programs = {
            'Охрана труда': 3,
            'Пожарная безопасность': 3,
            'Электробезопасность': 1,
            'Первая помощь': 3,
            'Ответственный за БДД': None,
            'Антитеррор': None
        }
        program_objects = {}
        for name, recurrence in programs.items():
            program, _ = TrainingProgram.objects.get_or_create(
                name=name,
                defaults={'recurrence_period': recurrence}
            )
            program_objects[name] = program
            logger.debug(f"Создана/получена программа обучения: {name}")
        for index, row in df.iterrows():
            logger.debug(f"Обрабатывается строка {index}")
            try:
                last_name = row.get(
                    ('Фамилия', 'Unnamed: 1_level_1', 'Unnamed: 1_level_2'), None)
                first_name = row.get(
                    ('Имя', 'Unnamed: 2_level_1', 'Unnamed: 2_level_2'), None)
                middle_name = row.get(
                    ('Отчество', 'Unnamed: 3_level_1', 'Unnamed: 3_level_2'), '') if pd.notna(
                    row.get(
                        ('Отчество', 'Unnamed: 3_level_1', 'Unnamed: 3_level_2'), None)) else ''
                position_name = row.get(
                    ('ДОЛЖНОСТЬ', 'Unnamed: 5_level_1', 'Unnamed: 5_level_2'), '') if pd.notna(
                    row.get(
                        ('ДОЛЖНОСТЬ', 'Unnamed: 5_level_1', 'Unnamed: 5_level_2'), None)) else ''
                department_name = row.get(
                    ('СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ',
                     'Unnamed: 6_level_1',
                     'Unnamed: 6_level_2'),
                    '') if pd.notna(
                    row.get(
                        ('СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ',
                         'Unnamed: 6_level_1',
                         'Unnamed: 6_level_2'),
                        None)) else ''
                note = row.get(
                    ('Примечание',
                     'Unnamed: 4_level_1',
                     'Unnamed: 4_level_2'),
                    '') if pd.notna(
                    row.get(
                        ('Примечание',
                         'Unnamed: 4_level_1',
                         'Unnamed: 4_level_2'),
                        None)) else ''
            except KeyError as e:
                logger.warning(
                    f"Ошибка доступа к столбцу в строке {index}: {e}")
                continue
            if pd.isna(last_name) or pd.isna(first_name):
                logger.warning(
                    f"Пропущена строка {index}: отсутствует Фамилия или Имя ({last_name}, {first_name})")
                continue
            logger.info(f"Обработка сотрудника: {last_name} {first_name}")
            is_dismissed = 'уволена' in note.lower()
            is_on_maternity_leave = 'декрет' in note.lower()
            is_safety_commission_member = 'член комиссии по охране труда' in note.lower()
            dismissal_date = None
            if is_dismissed and 'с ' in note.lower():
                try:
                    dismissal_date_str = note.lower().split('с ')[1].strip()
                    dismissal_date = datetime.strptime(
                        dismissal_date_str, '%d.%m.%Y').date()
                    logger.debug(
                        f"Обработана дата увольнения: {dismissal_date}")
                except (ValueError, IndexError):
                    logger.warning(
                        f"Не удалось разобрать дату увольнения для {last_name}: {note}")
            department, _ = Department.objects.get_or_create(
                name=department_name,
                defaults={'description': ''}
            )
            logger.debug(f"Создана/получена должность: {department_name}")
            position, _ = Position.objects.get_or_create(
                name=position_name,
                defaults={
                    'is_manager': 'руководитель' in position_name.lower(),
                    'is_teacher': 'преподаватель' in position_name.lower() or 'учитель' in position_name.lower()}
            )
            logger.debug(f"Создана/получена должность: {position_name}")
            employee, _ = Employee.objects.get_or_create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                defaults={
                    'position': position,
                    'department': department,
                    'is_dismissed': is_dismissed,
                    'is_on_maternity_leave': is_on_maternity_leave,
                    'is_safety_commission_member': is_safety_commission_member,
                    'dismissal_date': dismissal_date
                }
            )
            logger.info(f"Сотрудник добавлен/обновлен: {employee}")
            for program_name in programs.keys():
                program_obj = program_objects[program_name]
                for column in df.columns:
                    if column[0] == program_name and column[1] == 'Дата прохождения обучения':
                        cell_value = row.get(column, None)
                        if pd.notna(cell_value):
                            logger.debug(
                                f"Найдена дата для {program_name} в столбце {column}: {cell_value}")
                            cell_value = str(cell_value).strip()
                            entries = cell_value.split('\n')
                            for entry in entries:
                                entry = entry.strip()
                                if not entry:
                                    continue
                                details = ''
                                date_str = entry
                                has_question_mark = '?' in entry
                                if program_name == 'Электробезопасность' and ', ' in entry:
                                    try:
                                        details, date_str = entry.split(
                                            ', ', 1)
                                        date_str = date_str.strip()
                                    except ValueError:
                                        logger.warning(
                                            f"Ошибка обработки группы для {employee} ({program_name}): {entry}")
                                        continue
                                date_str = date_str.replace('?', '').strip()
                                try:
                                    if len(
                                            date_str) >= 10 and date_str[4] == '-' and date_str[7] == '-':
                                        training_date = datetime.strptime(
                                            date_str[:10], '%Y-%m-%d').date()
                                        logger.debug(
                                            f"Обработана дата YYYY-MM-DD: {training_date}")
                                    elif len(date_str) >= 8 and date_str[2] == '.' and date_str[5] == '.':
                                        training_date = datetime.strptime(
                                            date_str, '%d.%m.%Y').date()
                                        logger.debug(
                                            f"Обработана дата DD.MM.YYYY: {training_date}")
                                    else:
                                        logger.warning(
                                            f"Неподдерживаемый формат даты: {date_str}")
                                        continue
                                    if has_question_mark:
                                        details = f"{details} Отсутствует скан документа".strip(
                                        )
                                    TrainingRecord.objects.get_or_create(
                                        employee=employee,
                                        training_program=program_obj,
                                        completion_date=training_date,
                                        defaults={'details': details}
                                    )
                                    logger.info(
                                        f"Создана запись для {program_name}: {training_date} (Детали: {details})")
                                except (ValueError, TypeError) as e:
                                    logger.warning(
                                        f"Ошибка обработки даты для {employee} ({program_name}): {entry} ({e})")
                                    continue
        logger.info('Импорт данных успешно завершён!')
