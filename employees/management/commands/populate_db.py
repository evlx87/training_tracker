from datetime import date

from django.core.management.base import BaseCommand
from employees.models import Department, Position, TrainingProgram, Employee, TrainingRecord


class Command(BaseCommand):
    help = 'Заполняет базу данных предопределенными подразделениями и должностями'

    def handle(self, *args, **kwargs):
        # Список подразделений
        departments = [
            {"name": "Руководство", "description": "Руководство"},
            {"name": "УМО", "description": "Учебно-методический отдел"},
            {"name": "ООПиВР", "description": "Отдел общественно-политической и воспитательной работы"},
            {"name": "ОДО", "description": "Отдел дополнительного образования"},
            {"name": "ОСПР", "description": "Отдел социально-психологической работы"},
            {"name": "ОК", "description": "Отдел кадров"},
            {"name": "ФЭО", "description": "Финансово-экономический отдел"},
            {"name": "ОМТО", "description": "Отдел материально-технического обеспечения"},
            {"name": "ОДОб", "description": "Отдел документационного обеспечения"},
            {"name": "МО", "description": "Медицинский отдел"},
            {"name": "ООБ", "description": "Отдел обеспечения безопасности"},
            {"name": "ОПО", "description": "Отделение правового обеспечения"},
        ]

        # Список должностей
        positions = [
            {"name": "Директор"},
            {"name": "Первый заместитель директора"},
            {"name": "Заместитель директора (по учебно-методической работе)"},
            {"name": "Заместитель директора (по организационным вопросам и контролю)"},
            {"name": "Заместитель директора - руководитель отдела общественно-политической и воспитательной работы"},
            {"name": "Руководитель отдела"},
            {"name": "Заместитель руководителя отдела"},
            {"name": "Инспектор по инновационным технологиям"},
            {"name": "Старший методист"},
            {"name": "Методист"},
            {"name": "Учитель"},
            {"name": "Заместитель руководителя отдела (отделения Санкт-Петербургских кадетских классов и кадетских классов с морской направленностью)"},
            {"name": "Заместитель руководителя отдела (отделение кадетских классов Пансиона воспитанниц)"},
            {"name": "Старший воспитатель"},
            {"name": "Воспитатель"},
            {"name": "Педагог-организатор"},
            {"name": "Педагог дополнительного образования"},
            {"name": "Педагог дополнительного образования (заведующий музеем)"},
            {"name": "Педагог-библиотекарь (заведующий библиотекой)"},
            {"name": "Старший инспектор (психолог)"},
            {"name": "Педагог-психолог"},
            {"name": "Социальный педагог"},
            {"name": "Старший инспектор"},
            {"name": "Инспектор"},
            {"name": "Руководитель отдела (главный бухгалтер)"},
            {"name": "Инженер"},
            {"name": "Техник"},
            {"name": "Водитель автомобиля"},
            {"name": "Начальник отдела (врач-педиатр)"},
            {"name": "Врач-педиатр"},
            {"name": "Медицинская сестра"},
            {"name": "Инспектор (по охране труда)"},
            {"name": "Руководитель отделения"},
        ]

        # Список программ обучения
        training_programs = [
            {"name": "Охрана труда", "recurrence_period": 3},
            {"name": "Пожарная безопасность", "recurrence_period": 3},
            {"name": "Оказание первой помощи", "recurrence_period": 3},
        ]


        # Тестовые сотрудники
        employees = [
            {
                "last_name": "Иванов",
                "first_name": "Иван",
                "middle_name": "Иванович",
                "birth_date": date(1980, 1, 1),
                "position": "Директор",
                "department": "Руководство",
            },
            {
                "last_name": "Петрова",
                "first_name": "Анна",
                "middle_name": "Сергеевна",
                "birth_date": date(1985, 5, 15),
                "position": "Учитель",
                "department": "УМО",
            },
        ]

        # Тестовые записи об обучении
        training_records = [
            {
                "employee": {"last_name": "Иванов", "first_name": "Иван"},
                "training_program": "Охрана труда",
                "completion_date": date(2023, 6, 1),
            },
            {
                "employee": {"last_name": "Иванов", "first_name": "Иван"},
                "training_program": "Пожарная безопасность",
                "completion_date": date(2024, 3, 15),
            },
            {
                "employee": {"last_name": "Петрова", "first_name": "Анна"},
                "training_program": "Оказание первой помощи",
                "completion_date": date(2022, 9, 10),
            },
        ]


        # Заполнение подразделений
        self.stdout.write("Заполнение подразделений...")
        for dept in departments:
            # Проверяем, существует ли подразделение
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
            # Проверяем, существует ли должность
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
        for emp in employees:
            position = Position.objects.get(name=emp["position"])
            department = Department.objects.get(name=emp["department"])
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

        # Заполнение записей об обучении
        self.stdout.write("\nЗаполнение записей об обучении...")
        for record in training_records:
            employee = Employee.objects.get(
                last_name=record["employee"]["last_name"],
                first_name=record["employee"]["first_name"]
            )
            training_program = TrainingProgram.objects.get(name=record["training_program"])
            if not TrainingRecord.objects.filter(
                employee=employee,
                training_program=training_program,
                completion_date=record["completion_date"]
            ).exists():
                TrainingRecord.objects.create(
                    employee=employee,
                    training_program=training_program,
                    completion_date=record["completion_date"]
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Добавлена запись: {employee} - {training_program} ({record["completion_date"]})'
                ))
            else:
                self.stdout.write(
                    f'Запись "{employee} - {training_program} ({record["completion_date"]})" уже существует'
                )

        self.stdout.write(self.style.SUCCESS('\nЗаполнение базы данных завершено!'))