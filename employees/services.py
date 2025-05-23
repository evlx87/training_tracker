from datetime import timedelta
from django.utils import timezone
from .models import Employee, TrainingProgram, TrainingRecord

class ReportService:
    @staticmethod
    def generate_training_report():
        employees = Employee.objects.select_related('position', 'department').all()
        training_programs = TrainingProgram.objects.all()
        today = timezone.now().date()
        six_months = timedelta(days=180)
        report_data = []
        for employee in employees:
            employee_data = {'employee': employee, 'trainings': {}}
            for program in training_programs:
                latest_record = TrainingRecord.objects.filter(
                    employee=employee, training_program=program
                ).order_by('-completion_date').first()
                status = {'date': None, 'class': ''}
                if not latest_record:
                    status['date'] = 'Обучение не пройдено'
                    status['class'] = 'not-completed'
                else:
                    status['date'] = latest_record.completion_date
                    if program.recurrence_period:
                        due_date = latest_record.completion_date + timedelta(
                            days=program.recurrence_period * 365
                        )
                        warning_date = due_date - six_months
                        if today > due_date:
                            status['class'] = 'overdue'
                        elif today >= warning_date:
                            status['class'] = 'warning'
                employee_data['trainings'][program.id] = status
            report_data.append(employee_data)
        return report_data, training_programs