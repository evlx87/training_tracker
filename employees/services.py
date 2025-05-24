import logging
from django.core.cache import cache
from .models import Employee, TrainingProgram, TrainingRecord

logger = logging.getLogger('employees')

class ReportService:
    @staticmethod
    def generate_training_report():
        """
        Генерирует отчет по обучению, возвращая данные для таблицы и список программ.
        Использует кэширование для оптимизации производительности.
        """
        cache_key = 'training_report'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug('Отчет по обучению взят из кэша')
            return cached_data

        try:
            # Оптимизированный запрос с select_related и prefetch_related
            employees = Employee.objects.select_related('position', 'department').prefetch_related('trainingrecord_set__training_program')
            training_programs = TrainingProgram.objects.all()
            report_data = []

            for employee in employees:
                employee_data = {
                    'employee': employee,
                    'trainings': {}
                }
                for program in training_programs:
                    # Проверяем, есть ли запись об обучении для сотрудника по программе
                    record = employee.trainingrecord_set.filter(training_program=program).first()
                    employee_data['trainings'][program.id] = {
                        'completed': record.completion_date if record else None,
                        'status': 'Пройдено' if record else 'Не пройдено'
                    }
                report_data.append(employee_data)

            # Сохраняем в кэш на 15 минут
            cache.set(cache_key, (report_data, training_programs), timeout=60 * 15)
            logger.info('Сгенерирован отчет по обучению')
            return report_data, training_programs

        except Exception as e:
            logger.error('Ошибка при генерации отчета по обучению: %s', str(e))
            raise
