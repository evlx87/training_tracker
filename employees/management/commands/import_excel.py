import logging
import os

import pandas as pd
from dateutil.parser import parse as parse_date
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from employees.models import Employee, Department, Position, TrainingProgram, TrainingRecord

logger = logging.getLogger('employees')


class Command(BaseCommand):
    help = 'Импортирует данные из Excel файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=os.path.join(
                settings.BASE_DIR,
                'data_upload',
                'обучение.xlsx'),
            help='Путь к Excel-файлу для импорта'
        )

    def handle(self, *args, **kwargs):
        data_upload_dir = os.path.join(settings.BASE_DIR, 'data_upload')
        os.makedirs(data_upload_dir, exist_ok=True)
        file_path = kwargs['file']
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return
        try:
            df = pd.read_excel(file_path, header=[0, 1, 2], engine='openpyxl')
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {e}")
            return
        logger.info(f"Заголовки столбцов: {df.columns.tolist()}")

        # Динамическое определение программ
        programs = {}
        for column in df.columns:
            if column[1] == 'Дата прохождения обучения':
                program_name = column[0]
                programs[program_name] = 3 if program_name in [
                    'Охрана труда', 'Пожарная безопасность', 'Первая помощь'] else None

        program_objects = {}
        for name, recurrence in programs.items():
            program, _ = TrainingProgram.objects.get_or_create(
                name=name,
                defaults={'recurrence_period': recurrence}
            )
            program_objects[name] = program
            logger.debug(f"Создана/получена программа обучения: {name}")

        # Нормализация заголовков
        column_mapping = {
            'Фамилия': None, 'Имя': None, 'Отчество': None,
            'ДОЛЖНОСТЬ': None, 'СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ': None, 'Примечание': None
        }
        for col in df.columns:
            if col[0] in column_mapping:
                column_mapping[col[0]] = col
        missing_cols = [
            key for key,
            value in column_mapping.items() if value is None]
        if missing_cols:
            logger.error(f"Отсутствуют обязательные столбцы: {missing_cols}")
            return

        for index, row in df.iterrows():
            with transaction.atomic():
                logger.debug(f"Обрабатывается строка {index}")
                last_name = row.get(column_mapping['Фамилия'], None)
                first_name = row.get(column_mapping['Имя'], None)
                middle_name = row.get(
                    column_mapping['Отчество'],
                    '') if pd.notna(
                    row.get(
                        column_mapping['Отчество'],
                        None)) else ''
                position_name = row.get(
                    column_mapping['ДОЛЖНОСТЬ'],
                    '') if pd.notna(
                    row.get(
                        column_mapping['ДОЛЖНОСТЬ'],
                        None)) else ''
                department_name = row.get(
                    column_mapping['СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ'],
                    '') if pd.notna(
                    row.get(
                        column_mapping['СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ'],
                        None)) else ''
                note = row.get(
                    column_mapping['Примечание'],
                    '') if pd.notna(
                    row.get(
                        column_mapping['Примечание'],
                        None)) else ''

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
                        dismissal_date_str = note.lower().split('с ')[
                            1].strip()
                        dismissal_date = parse_date(
                            dismissal_date_str, dayfirst=True).date()
                        logger.debug(
                            f"Обработана дата увольнения: {dismissal_date}")
                    except ValueError:
                        logger.warning(
                            f"Не удалось разобрать дату увольнения для {last_name}: {note}")

                department = None
                if department_name.strip():
                    department, _ = Department.objects.get_or_create(
                        name=department_name,
                        defaults={'description': ''}
                    )
                    logger.debug(
                        f"Создана/получена должность: {department_name}")

                position = None
                if position_name.strip():
                    position, _ = Position.objects.get_or_create(
                        name=position_name,
                        defaults={
                            'is_manager': 'руководитель' in position_name.lower(),
                            'is_teacher': 'преподаватель' in position_name.lower() or 'учитель' in position_name.lower()
                        }
                    )
                    logger.debug(
                        f"Создана/получена должность: {position_name}")

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
                                    try:
                                        training_date = parse_date(
                                            date_str, dayfirst=True).date()
                                        logger.debug(
                                            f"Обработана дата: {training_date} для {employee} ({program_name})")
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
                                    except ValueError:
                                        logger.warning(
                                            f"Неподдерживаемый формат даты: {date_str} для {employee} ({program_name})")
                                        continue
        logger.info('Импорт данных успешно завершён!')
