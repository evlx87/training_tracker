import pandas as pd
from datetime import datetime
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from employees.models import Employee, Department, Position, TrainingProgram, TrainingRecord


class Command(BaseCommand):
    help = 'Импортирует данные из Excel файла в базу данных'

    def handle(self, *args, **kwargs):
        # Путь к файлу в корне проекта
        file_path = os.path.join(settings.BASE_DIR, 'data_upload', 'обучение.xlsx')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл не найден: {file_path}"))
            return

        # Чтение Excel файла
        try:
            df = pd.read_excel(file_path, header=[0, 1, 2], engine='openpyxl')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка чтения файла: {e}"))
            return

        # Вывод заголовков для диагностики
        self.stdout.write(self.style.WARNING(f"Заголовки столбцов: {df.columns.tolist()}"))

        # Список программ обучения с периодичностью
        programs = {
            'Охрана труда': 3,
            'Пожарная безопасность': 3,
            'Электробезопасность': 3,
            'Первая помощь': 3,
            'Ответственный за БДД': None,
            'Антитеррор': None
        }

        # Создание программ обучения
        program_objects = {}
        for name, recurrence in programs.items():
            program, _ = TrainingProgram.objects.get_or_create(
                name=name,
                defaults={'recurrence_period': recurrence}
            )
            program_objects[name] = program

        # Обработка строк таблицы
        for index, row in df.iterrows():
            self.stdout.write(self.style.WARNING(f"Обрабатывается строка {index}"))

            # Попытка доступа к данным сотрудника
            try:
                last_name = row.get(('Фамилия', 'Unnamed: 1_level_1', 'Unnamed: 1_level_2'), None)
                first_name = row.get(('Имя', 'Unnamed: 2_level_1', 'Unnamed: 2_level_2'), None)
                middle_name = row.get(('Отчество', 'Unnamed: 3_level_1', 'Unnamed: 3_level_2'), '') if pd.notna(
                    row.get(('Отчество', 'Unnamed: 3_level_1', 'Unnamed: 3_level_2'), None)) else ''
                position_name = row.get(('ДОЛЖНОСТЬ', 'Unnamed: 5_level_1', 'Unnamed: 5_level_2'), '') if pd.notna(
                    row.get(('ДОЛЖНОСТЬ', 'Unnamed: 5_level_1', 'Unnamed: 5_level_2'), None)) else ''
                department_name = row.get(('СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ', 'Unnamed: 6_level_1', 'Unnamed: 6_level_2'),
                                          '') if pd.notna(
                    row.get(('СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ', 'Unnamed: 6_level_1', 'Unnamed: 6_level_2'), None)) else ''
                note = row.get(('Примечание', 'Unnamed: 4_level_1', 'Unnamed: 4_level_2'), '') if pd.notna(
                    row.get(('Примечание', 'Unnamed: 4_level_1', 'Unnamed: 4_level_2'), None)) else ''
            except KeyError as e:
                self.stdout.write(self.style.WARNING(f"Ошибка доступа к столбцу в строке {index}: {e}"))
                continue

            # Пропуск строк без ФИО
            if pd.isna(last_name) or pd.isna(first_name):
                self.stdout.write(self.style.WARNING(
                    f"Пропущена строка {index}: отсутствует Фамилия или Имя ({last_name}, {first_name})"))
                continue

            self.stdout.write(self.style.WARNING(f"Обработка сотрудника: {last_name} {first_name}"))

            # Обработка статуса сотрудника
            is_dismissed = 'уволена' in note.lower()
            is_on_maternity_leave = 'декрет' in note.lower()
            dismissal_date = None
            if is_dismissed and 'с ' in note.lower():
                try:
                    dismissal_date_str = note.lower().split('с ')[1].strip()
                    dismissal_date = datetime.strptime(dismissal_date_str, '%d.%m.%Y').date()
                except (ValueError, IndexError):
                    self.stdout.write(
                        self.style.WARNING(f"Не удалось разобрать дату увольнения для {last_name}: {note}"))

            # Создание или получение подразделения
            department, _ = Department.objects.get_or_create(
                name=department_name,
                defaults={'description': ''}
            )

            # Создание или получение должности
            position, _ = Position.objects.get_or_create(
                name=position_name
            )

            # Создание или получение сотрудника
            employee, _ = Employee.objects.get_or_create(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                defaults={
                    'position': position,
                    'department': department,
                    'is_dismissed': is_dismissed,
                    'is_on_maternity_leave': is_on_maternity_leave,
                    'dismissal_date': dismissal_date
                }
            )

            # Обработка программ обучения
            for program_name in programs.keys():
                program_obj = program_objects[program_name]

                # Проверка всех возможных столбцов для программы
                for column in df.columns:
                    if column[0] == program_name and column[1] == 'Дата прохождения обучения':
                        cell_value = row.get(column, None)
                        if pd.notna(cell_value):
                            self.stdout.write(
                                self.style.WARNING(f"Найдена дата для {program_name} в столбце {column}: {cell_value}"))
                            # Обработка строки
                            cell_value = str(cell_value).strip()
                            # Разделяем множественные даты или группы
                            entries = cell_value.split('\n')
                            for entry in entries:
                                entry = entry.strip()
                                if not entry:
                                    continue
                                details = ''
                                date_str = entry
                                has_question_mark = '?' in entry

                                # Для электробезопасности извлекаем группу
                                if program_name == 'Электробезопасность' and ', ' in entry:
                                    try:
                                        details, date_str = entry.split(', ', 1)
                                        date_str = date_str.strip()
                                    except ValueError:
                                        self.stdout.write(self.style.WARNING(
                                            f"Ошибка обработки группы для {employee} ({program_name}): {entry}"))
                                        continue
                                # Убираем символ '?' из даты
                                date_str = date_str.replace('?', '').strip()

                                # Обработка даты
                                try:
                                    # Формат YYYY-MM-DD HH:MM:SS
                                    if len(date_str) >= 10 and date_str[4] == '-' and date_str[7] == '-':
                                        training_date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
                                        self.stdout.write(
                                            self.style.WARNING(f"Обработана дата YYYY-MM-DD: {training_date}"))
                                    # Формат DD.MM.YYYY
                                    elif len(date_str) >= 8 and date_str[2] == '.' and date_str[5] == '.':
                                        training_date = datetime.strptime(date_str, '%d.%m.%Y').date()
                                        self.stdout.write(
                                            self.style.WARNING(f"Обработана дата DD.MM.YYYY: {training_date}"))
                                    else:
                                        self.stdout.write(
                                            self.style.WARNING(f"Неподдерживаемый формат даты: {date_str}"))
                                        continue

                                    # Добавляем пометку об отсутствии скана, если есть '?'
                                    if has_question_mark:
                                        details = f"{details} Отсутствует скан документа".strip()

                                    # Создание записи
                                    TrainingRecord.objects.get_or_create(
                                        employee=employee,
                                        training_program=program_obj,
                                        completion_date=training_date,
                                        defaults={'details': details}
                                    )
                                    self.stdout.write(self.style.WARNING(
                                        f"Создана запись для {program_name}: {training_date} (Детали: {details})"))
                                except (ValueError, TypeError) as e:
                                    self.stdout.write(self.style.WARNING(
                                        f"Ошибка обработки даты для {employee} ({program_name}): {entry} ({e})"))
                                    continue

        self.stdout.write(self.style.SUCCESS('Импорт данных успешно завершён!'))