from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models import Q
from employees.models import Employee, TrainingProgram, TrainingRecord
import logging

logger = logging.getLogger('employees')

class ReportService:
    @staticmethod
    def generate_training_report(selected_employees=None, selected_program=None):
        logger.debug("Generating training report")
        report_data = []
        training_programs = TrainingProgram.objects.all().order_by('name')
        employees_query = Employee.objects.filter(Q(is_dismissed=False) | Q(dismissal_date__isnull=True)).select_related('department').order_by('last_name', 'first_name')
        if selected_employees and selected_employees[0]:  # Пропускаем случай "Все сотрудники"
            employees_query = employees_query.filter(pk__in=[int(emp) for emp in selected_employees])
        today = datetime.now().date()

        logger.debug("Training programs in report: %s", [program.name for program in training_programs])
        logger.debug("Employees count: %s", employees_query.count())

        for employee in employees_query:
            employee_data = {
                'employee': employee,
                'trainings': {program.id: {'date': "Обучение не пройдено", 'class': 'not-completed', 'details': ""} for program in training_programs}
            }
            # Фильтрация записей по selected_program, если указано
            records = employee.trainingrecord_set.all().select_related('training_program')
            if selected_program and selected_program.isdigit():
                records = records.filter(training_program_id=int(selected_program))
            for record in records:
                program = record.training_program
                status_class = 'not-completed'
                status_date = record.completion_date
                details = record.details or ""
                if program.recurrence_period:
                    expiry_date = record.completion_date + relativedelta(years=program.recurrence_period)
                    warning_date = expiry_date - relativedelta(months=1)
                    if today > expiry_date:
                        status_class = 'overdue'
                    elif today >= warning_date:
                        status_class = 'warning'
                    else:
                        status_class = 'completed'
                else:
                    status_class = 'completed'
                employee_data['trainings'][program.id] = {
                    'date': status_date,
                    'class': status_class,
                    'details': details
                }
            report_data.append(employee_data)
            logger.debug("Employee %s trainings: %s", employee.last_name, employee_data['trainings'])

        logger.debug("Training report generated successfully")
        logger.debug("Generated report_data: %s", [data['employee'].last_name for data in report_data])
        return report_data, training_programs