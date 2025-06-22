import logging
from datetime import date, timedelta

from employees.models import Employee, TrainingRecord
from trainings.models import TrainingProgram

logger = logging.getLogger('reports')

class ReportService:
    @staticmethod
    def generate_training_report(selected_employees=None, selected_program=None):
        employees = Employee.objects.all()
        training_programs = TrainingProgram.objects.all()
        report_data = []

        if selected_employees:
            employees = employees.filter(pk__in=selected_employees)

        for employee in employees:
            employee_data = {'employee': employee, 'trainings': {}}
            for program in training_programs:
                if selected_program and str(program.id) != selected_program:
                    continue
                records = TrainingRecord.objects.filter(
                    employee=employee, training_program=program
                ).order_by('-completion_date')
                if records.exists():
                    latest_record = records.first()
                    status_class = 'completed'
                    # Проверяем, есть ли training_program и recurrence_period
                    if hasattr(latest_record, 'training_program') and latest_record.training_program.recurrence_period is not None:
                        next_training_date = latest_record.completion_date + timedelta(
                            days=latest_record.training_program.recurrence_period * 365
                        )
                        today = date.today()
                        warning_date = next_training_date - timedelta(days=30)
                        if today > next_training_date:
                            status_class = 'overdue'
                        elif today >= warning_date:
                            status_class = 'warning'
                    else:
                        # Если recurrence_period не задан, оставляем статус completed
                        logger.debug(f"No recurrence_period for TrainingProgram {latest_record.training_program} (Employee: {employee})")
                    employee_data['trainings'][program.id] = {
                        'date': latest_record.completion_date,
                        'class': status_class,
                        'is_verified': latest_record.is_verified
                    }
                else:
                    employee_data['trainings'][program.id] = {
                        'date': "Обучение не пройдено",
                        'class': 'not-completed',
                        'is_verified': False
                    }
            report_data.append(employee_data)

        return report_data, training_programs