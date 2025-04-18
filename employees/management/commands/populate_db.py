from django.core.management.base import BaseCommand

from data_upload.departments_list import departments
from data_upload.employees_list import employees_data_list
from data_upload.positions_list import positions
from data_upload.training_programs_list import training_programs
from employees.models import Department, Position, TrainingProgram, Employee


class Command(BaseCommand):
    help = 'Заполняет базу данных предопределенными подразделениями и должностями'

    def handle(self, *args, **kwargs):
    # Заполнение подразделений
        self.stdout.write("Заполнение подразделений...")
        for dept in departments:
            if not Department.objects.filter(name=dept["name"]).exists():
                Department.objects.create(
                    name=dept["name"],
                    description=dept["description"]
                )
                self.stdout.write(self.style.SUCCESS(f'Добавлено подразделение: {dept["name"]}'))
            else:
                self.stdout.write(f'Подразделение "{dept["name"]}" уже существует')

        # Заполнение должностей
        self.stdout.write("\nЗаполнение должностей...")
        for pos in positions:
            if not Position.objects.filter(name=pos["name"]).exists():
                Position.objects.create(name=pos["name"])
                self.stdout.write(self.style.SUCCESS(f'Добавлена должность: {pos["name"]}'))
            else:
                self.stdout.write(f'Должность "{pos["name"]}" уже существует')

        # Заполнение программ обучения
        self.stdout.write("\nЗаполнение программ обучения...")
        for prog in training_programs:
            if not TrainingProgram.objects.filter(name=prog["name"]).exists():
                TrainingProgram.objects.create(
                    name=prog["name"],
                    recurrence_period=prog["recurrence_period"]
                )
                self.stdout.write(self.style.SUCCESS(f'Добавлена программа: {prog["name"]}'))
            else:
                self.stdout.write(f'Программа "{prog["name"]}" уже существует')

        # Заполнение сотрудников
        self.stdout.write("\nЗаполнение сотрудников...")
        for emp in employees_data_list:
            # Проверяем и создаём должность, если она отсутствует
            if emp["position"]:
                position, created = Position.objects.get_or_create(name=emp["position"])
                if created:
                    self.stdout.write(self.style.WARNING(f'Создана новая должность: {emp["position"]}'))
            else:
                position = None  # Если должность не указана

            # Проверяем и создаём подразделение, если оно отсутствует
            if emp["department"]:
                department, created = Department.objects.get_or_create(
                    name=emp["department"],
                    defaults={"description": emp["department"]}  # Описание по умолчанию
                )
                if created:
                    self.stdout.write(self.style.WARNING(f'Создано новое подразделение: {emp["department"]}'))
            else:
                department = None  # Если подразделение не указано

            if not Employee.objects.filter(last_name=emp["last_name"], first_name=emp["first_name"]).exists():
                Employee.objects.create(
                    last_name=emp["last_name"],
                    first_name=emp["first_name"],
                    middle_name=emp["middle_name"],
                    birth_date=emp["birth_date"],
                    position=position,
                    department=department,
                )
                self.stdout.write(self.style.SUCCESS(f'Добавлен сотрудник: {emp["last_name"]} {emp["first_name"]}'))
            else:
                self.stdout.write(f'Сотрудник "{emp["last_name"]} {emp["first_name"]}" уже существует')

        # # Заполнение записей об обучении
        # self.stdout.write("\nЗаполнение записей об обучении...")
        # for record in training_records:
        #     try:
        #         employee = Employee.objects.get(
        #             last_name=record["employee"]["last_name"],
        #             first_name=record["employee"]["first_name"]
        #         )
        #         training_program = TrainingProgram.objects.get(name=record["training_program"])
        #         if not TrainingRecord.objects.filter(
        #             employee=employee,
        #             training_program=training_program,
        #             completion_date=record["completion_date"]
        #         ).exists():
        #             TrainingRecord.objects.create(
        #                 employee=employee,
        #                 training_program=training_program,
        #                 completion_date=record["completion_date"]
        #             )
        #             self.stdout.write(self.style.SUCCESS(
        #                 f'Добавлена запись: {employee} - {training_program} ({record["completion_date"]})'
        #             ))
        #         else:
        #             self.stdout.write(
        #                 f'Запись "{employee} - {training_program} ({record["completion_date"]})" уже существует'
        #             )
        #     except Employee.DoesNotExist:
        #         self.stdout.write(self.style.ERROR(
        #             f'Сотрудник {record["employee"]["last_name"]} {record["employee"]["first_name"]} не найден'
        #         ))

        self.stdout.write(self.style.SUCCESS('\nЗаполнение базы данных завершено!'))