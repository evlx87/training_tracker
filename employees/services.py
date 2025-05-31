import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db import models
from .models import Employee, TrainingProgram, TrainingRecord

logger = logging.getLogger('employees')


class ReportService:
    @staticmethod
    def generate_training_report(department_id=None, search_query=None):
        """
        Генерирует отчет по обучению, возвращая данные для таблицы и список программ.
        Учитывает статусы: не пройдено, просрочено, скоро истекает, пройдено.
        Поддерживает фильтрацию по подразделению и поиск по имени.
        Использует кэширование для оптимизации производительности.
        """
        cache_key = f'training_report_{department_id}_{search_query}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug('Отчет по обучению взят из кэша: %s', cache_key)
            return cached_data

        try:
            # Оптимизированный запрос с фильтрацией
            queryset = Employee.objects.select_related(
                'position', 'department').prefetch_related('trainingrecord_set__training_program')
            if department_id:
                queryset = queryset.filter(department_id=department_id)
            if search_query:
                queryset = queryset.filter(
                    models.Q(last_name__icontains=search_query) |
                    models.Q(first_name__icontains=search_query) |
                    models.Q(middle_name__icontains=search_query)
                )
            employees = queryset
            training_programs = TrainingProgram.objects.all()
            report_data = []
            today = date.today()

            for employee in employees:
                employee_data = {
                    'employee': employee,
                    'trainings': {}
                }
                for program in training_programs:
                    record = employee.trainingrecord_set.filter(
                        training_program=program).order_by('-completion_date').first()
                    status_class = 'not-completed'
                    status_date = "Обучение не пройдено"
                    details = ""

                    if record:
                        status_date = record.completion_date
                        details = record.details or ""
                        if program.recurrence_period:
                            expiry_date = record.completion_date + \
                                relativedelta(years=program.recurrence_period)
                            warning_date = expiry_date - \
                                relativedelta(months=1)
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

            # Сохраняем в кэш на 15 минут
            cache.set(
                cache_key,
                (report_data,
                 training_programs),
                timeout=60 * 15)
            logger.info(
                'Сгенерирован отчет по обучению: %d сотрудников, %d программ',
                len(report_data),
                len(training_programs))
            return report_data, training_programs

        except Exception as e:
            logger.error('Ошибка при генерации отчета по обучению: %s', str(e))
            raise
