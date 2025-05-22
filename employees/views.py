import logging
from datetime import timedelta
from django.contrib import messages
from django.forms import ModelForm, TextInput, Textarea
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import EmployeeForm, DepartmentForm, PositionForm, TrainingProgramForm, TrainingRecordForm
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord

# Настройка логгера
logger = logging.getLogger('employees')

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': TextInput(attrs={'class': 'form-input'}),
            'description': Textarea(attrs={'class': 'form-textarea'}),
        }

class PositionForm(ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-input'}),
        }

def index(request):
    logger.info('Открыта главная страница')
    return render(request, 'index.html')

def employee_list(request):
    logger.info('Запрошен список сотрудников')
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            logger.info(f'Создан сотрудник: {employee}')
            return redirect('employees:employee_list')
        else:
            logger.warning(f'Ошибка валидации формы создания сотрудника: {form.errors}')
    else:
        form = EmployeeForm()
        logger.debug('Открыта форма создания сотрудника')
    return render(request, 'employee_form.html', {'form': form, 'action': 'Добавить'})

def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            logger.info(f'Обновлен сотрудник: {employee}')
            return redirect('employees:employee_list')
        else:
            logger.warning(f'Ошибка валидации формы редактирования сотрудника: {form.errors}')
    else:
        form = EmployeeForm(instance=employee)
        logger.debug(f'Открыта форма редактирования сотрудника: {employee}')
    return render(request, 'employee_form.html', {'form': form, 'action': 'Редактировать'})

def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        logger.info(f'Удален сотрудник: {employee}')
        employee.delete()
        return redirect('employees:employee_list')
    logger.debug(f'Открыта страница подтверждения удаления сотрудника: {employee}')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

def employee_trainings(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    training_records = TrainingRecord.objects.filter(employee=employee)
    logger.info(f'Запрошены записи об обучении для сотрудника: {employee}')
    return render(request, 'employee_trainings.html', {
        'employee': employee,
        'training_records': training_records
    })

def training_record_create(request):
    employee_pk = request.GET.get('employee_pk')
    if not employee_pk:
        logger.error('Не указан сотрудник для создания записи об обучении')
        messages.error(request, 'Пожалуйста, выберите сотрудника.')
        return redirect('employees:employee_list')
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            training_record = form.save(commit=False)
            training_record.employee = employee
            training_record.save()
            logger.info(f'Создана запись об обучении для {employee}: {training_record}')
            return redirect('employees:employee_trainings', pk=employee_pk)
        else:
            logger.warning(f'Ошибка валидации формы создания записи об обучении: {form.errors}')
    else:
        form = TrainingRecordForm()
        logger.debug(f'Открыта форма создания записи об обучении для сотрудника: {employee}')
    return render(request, 'training_record_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Добавить'
    })

def training_record_edit(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, instance=training_record)
        if form.is_valid():
            training_record = form.save()
            logger.info(f'Обновлена запись об обучении для {employee}: {training_record}')
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            logger.warning(f'Ошибка валидации формы редактирования записи об обучении: {form.errors}')
    else:
        form = TrainingRecordForm(instance=training_record)
        logger.debug(f'Открыта форма редактирования записи об обучении: {training_record}')
    return render(request, 'training_record_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Редактировать'
    })

def training_record_delete(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        logger.info(f'Удалена запись об обучении: {training_record}')
        training_record.delete()
        return redirect('employees:employee_trainings', pk=employee.pk)
    logger.debug(f'Открыта страница подтверждения удаления записи об обучении: {training_record}')
    return render(request, 'training_record_confirm_delete.html', {
        'training_record': training_record,
        'employee': employee
    })

def department_list(request):
    departments = Department.objects.all()
    logger.info('Запрошен список подразделений')
    return render(request, 'departments.html', {'departments': departments})

def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            logger.info(f'Создано подразделение: {department}')
            return redirect('employees:department_list')
        else:
            logger.warning(f'Ошибка валидации формы создания подразделения: {form.errors}')
    else:
        form = DepartmentForm()
        logger.debug('Открыта форма создания подразделения')
    return render(request, 'department_form.html', {'form': form, 'action': 'Добавить'})

def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            logger.info(f'Обновлено подразделение: {department}')
            return redirect('employees:department_list')
        else:
            logger.warning(f'Ошибка валидации формы редактирования подразделения: {form.errors}')
    else:
        form = DepartmentForm(instance=department)
        logger.debug(f'Открыта форма редактирования подразделения: {department}')
    return render(request, 'department_form.html', {'form': form, 'action': 'Редактировать'})

def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        logger.info(f'Удалено подразделение: {department}')
        department.delete()
        return redirect('employees:department_list')
    logger.debug(f'Открыта страница подтверждения удаления подразделения: {department}')
    return render(request, 'department_confirm_delete.html', {'department': department})

def position_list(request):
    positions = Position.objects.all()
    logger.info('Запрошен список должностей')
    return render(request, 'positions.html', {'positions': positions})

def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            logger.info(f'Создана должность: {position}')
            return redirect('employees:position_list')
        else:
            logger.warning(f'Ошибка валидации формы создания должности: {form.errors}')
    else:
        form = PositionForm()
        logger.debug('Открыта форма создания должности')
    return render(request, 'position_form.html', {'form': form, 'action': 'Добавить'})

def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
            logger.info(f'Обновлена должность: {position}')
            return redirect('employees:position_list')
        else:
            logger.warning(f'Ошибка валидации формы редактирования должности: {form.errors}')
    else:
        form = PositionForm(instance=position)
        logger.debug(f'Открыта форма редактирования должности: {position}')
    return render(request, 'position_form.html', {'form': form, 'action': 'Редактировать'})

def position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        logger.info(f'Удалена должность: {position}')
        position.delete()
        return redirect('employees:position_list')
    logger.debug(f'Открыта страница подтверждения удаления должности: {position}')
    return render(request, 'position_confirm_delete.html', {'position': position})

def training_list(request):
    trainings = TrainingProgram.objects.all()
    logger.info('Запрошен список программ обучения')
    return render(request, 'trainings.html', {'trainings': trainings})

def training_create(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            training = form.save()
            logger.info(f'Создана программа обучения: {training}')
            return redirect('employees:training_list')
        else:
            logger.warning(f'Ошибка валидации формы создания программы обучения: {form.errors}')
    else:
        form = TrainingProgramForm()
        logger.debug('Открыта форма создания программы обучения')
    return render(request, 'training_form.html', {'form': form, 'action': 'Добавить'})

def training_edit(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=training)
        if form.is_valid():
            training = form.save()
            logger.info(f'Обновлена программа обучения: {training}')
            return redirect('employees:training_list')
        else:
            logger.warning(f'Ошибка валидации формы редактирования программы обучения: {form.errors}')
    else:
        form = TrainingProgramForm(instance=training)
        logger.debug(f'Открыта форма редактирования программы обучения: {training}')
    return render(request, 'training_form.html', {'form': form, 'action': 'Редактировать'})

def training_delete(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        logger.info(f'Удалена программа обучения: {training}')
        training.delete()
        return redirect('employees:training_list')
    logger.debug(f'Открыта страница подтверждения удаления программы обучения: {training}')
    return render(request, 'training_confirm_delete.html', {'training': training})

def reports(request):
    employees = Employee.objects.select_related('position', 'department').all()
    training_programs = TrainingProgram.objects.all()
    today = timezone.now().date()
    six_months = timedelta(days=180)
    report_data = []
    for employee in employees:
        employee_data = {
            'employee': employee,
            'trainings': {}
        }
        for program in training_programs:
            latest_record = TrainingRecord.objects.filter(
                employee=employee,
                training_program=program
            ).order_by('-completion_date').first()
            status = {
                'date': None,
                'class': ''
            }
            if not latest_record:
                status['date'] = 'Обучение не пройдено'
                status['class'] = 'not-completed'
            else:
                status['date'] = latest_record.completion_date
                if program.recurrence_period:
                    due_date = latest_record.completion_date + \
                        timedelta(days=program.recurrence_period * 365)
                    warning_date = due_date - six_months
                    if today > due_date:
                        status['class'] = 'overdue'
                    elif today >= warning_date:
                        status['class'] = 'warning'
            employee_data['trainings'][program.id] = status
        report_data.append(employee_data)
    logger.info('Запрошен отчет по обучению')
    return render(request, 'reports.html', {
        'report_data': report_data,
        'training_programs': training_programs,
        'employees': employees
    })