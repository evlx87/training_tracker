import pandas as pd
from datetime import datetime, date

# Чтение Excel-файла
# Замените 'employees.xlsx' на путь к вашему Excel-файлу
df = pd.read_excel('employees.xlsx')

# Выводим названия столбцов для диагностики
print("Названия столбцов в Excel-файле:", df.columns.tolist())

# Функция для извлечения даты из строки
def parse_date(date_value):
    # Если значение пустое или None, возвращаем None
    if pd.isna(date_value):
        return None

    # Если значение уже является объектом datetime (Excel может автоматически преобразовать дату)
    if isinstance(date_value, datetime):
        return date(date_value.year, date_value.month, date_value.day)

    # Если значение — число (Excel может хранить даты как числа)
    if isinstance(date_value, (int, float)):
        try:
            return (datetime(1899, 12, 30) + pd.Timedelta(days=date_value)).date()
        except ValueError:
            print(f"Не удалось преобразовать число в дату: {date_value}")
            return None

    # Если значение строка, пробуем распарсить
    date_str = str(date_value).strip()
    if not date_str:
        return None

    # Извлекаем первую часть строки (например, "05.01.1981 Воспитатель" -> "05.01.1981")
    date_part = date_str.split()[0]

    # Пробуем разные форматы дат
    for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'):
        try:
            parsed_date = datetime.strptime(date_part, fmt)
            return date(parsed_date.year, parsed_date.month, parsed_date.day)
        except ValueError:
            continue

    # Если ни один формат не подошёл, выводим значение для диагностики
    print(f"Не удалось распарсить дату: {date_str}")
    return None

# Создаём список сотрудников
employees = []

# Проходим по каждой строке таблицы
for index, row in df.iterrows():
    # Извлекаем данные из строки
    last_name = row['last_name'] if not pd.isna(row['last_name']) else ''
    first_name = row['first_name'] if not pd.isna(row['first_name']) else ''
    middle_name = row['middle_name'] if not pd.isna(row['middle_name']) else ''
    birth_date = parse_date(row['birth_date'])
    position = row['position'] if not pd.isna(row['position']) else ''
    department = row['department'] if not pd.isna(row['department']) else ''

    # Создаём словарь для сотрудника
    employee = {
        "last_name": str(last_name),
        "first_name": str(first_name),
        "middle_name": str(middle_name),
        "birth_date": birth_date,  # Оставляем None, если дата не указана
        "position": str(position),
        "department": str(department),
    }

    # Добавляем сотрудника в список
    employees.append(employee)

# Выводим результат
print("\nemployees = [")
for emp in employees:
    print(f"    {{")
    print(f"        \"last_name\": \"{emp['last_name']}\",")
    print(f"        \"first_name\": \"{emp['first_name']}\",")
    print(f"        \"middle_name\": \"{emp['middle_name']}\",")
    if emp['birth_date'] is None:
        print(f"        \"birth_date\": None,")
    else:
        print(f"        \"birth_date\": date({emp['birth_date'].year}, {emp['birth_date'].month}, {emp['birth_date'].day}),")
    print(f"        \"position\": \"{emp['position']}\",")
    print(f"        \"department\": \"{emp['department']}\",")
    print(f"    }},")
print("]")

# Сохраняем результат в файл
with open('employees_output.py', 'w', encoding='utf-8') as f:
    f.write("from datetime import date\n\n")
    f.write("employees = [\n")
    for emp in employees:
        f.write(f"    {{\n")
        f.write(f"        \"last_name\": \"{emp['last_name']}\",\n")
        f.write(f"        \"first_name\": \"{emp['first_name']}\",\n")
        f.write(f"        \"middle_name\": \"{emp['middle_name']}\",\n")
        if emp['birth_date'] is None:
            f.write(f"        \"birth_date\": None,\n")
        else:
            f.write(f"        \"birth_date\": date({emp['birth_date'].year}, {emp['birth_date'].month}, {emp['birth_date'].day}),\n")
        f.write(f"        \"position\": \"{emp['position']}\",\n")
        f.write(f"        \"department\": \"{emp['department']}\",\n")
        f.write(f"    }},\n")
    f.write("]\n")