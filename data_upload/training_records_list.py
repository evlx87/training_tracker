# Тестовые записи об обучении (используем реальных сотрудников из employees_data_list)
from datetime import date

training_records = [
    {
        "employee": {"last_name": "Акимов", "first_name": "Дмитрий"},
        "training_program": "Охрана труда",
        "completion_date": date(2023, 6, 1),
    },
    {
        "employee": {"last_name": "Акимов", "first_name": "Дмитрий"},
        "training_program": "Пожарная безопасность",
        "completion_date": date(2024, 3, 15),
    },
    {
        "employee": {"last_name": "Алейникова", "first_name": "Ирина"},
        "training_program": "Оказание первой помощи",
        "completion_date": date(2022, 9, 10),
    },
]