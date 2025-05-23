import logging
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
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

@login_required
def index(request):
    logger.info('Открыта главная страница пользователем: %s', request.user.username)
    return render(request, 'index.html')

@login_required
def employee_list(request):
    logger.info('Запрошен список сотрудников пользователем: %s', request.user.username)
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})

@login_required
@permission_required('employees.add_employee', raise_exception=True)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            logger.info('Создан сотрудник: %s пользователем: %s', employee, request.user.username)
            return redirect('employees:employee_list')
        else:
            logger.warning('Ошибка валидации формы создания сотрудника: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = EmployeeForm()
        logger.debug('Открыта форма создания сотрудника пользователем: %s', request.user.username)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Добавить'})

@login_required
@permission_required('employees.change_employee', raise_exception=True)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            logger.info('Обновлен сотрудник: %s пользователем: %s', employee, request.user.username)
            return redirect('employees:employee_list')
        else:
            logger.warning('Ошибка валидации формы редактирования сотрудника: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = EmployeeForm(instance=employee)
        logger.debug('Открыта форма редактирования сотрудника: %s пользователем: %s', employee, request.user.username)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Редактировать'})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_employee'):
            logger.info('Удален сотрудник: %s пользователем: %s', employee, request.user.username)
            employee.delete()
            return redirect('employees:employee_list')
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:employee_delete_confirm', pk=pk)
    logger.debug('Открыта страница подтверждения удаления сотрудника: %s пользователем: %s', employee, request.user.username)
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_delete_confirm(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление сотрудника: %s пользователем mto', employee)
            employee.delete()
            return redirect('employees:employee_list')
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
    return render(request, 'employee_confirm_delete.html', {'employee': employee, 'confirm_mode': True})

@login_required
def employee_trainings(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    training_records = TrainingRecord.objects.filter(employee=employee)
    logger.info('Запрошены записи об обучении для сотрудника: %s пользователем: %s', employee, request.user.username)
    return render(request, 'employee_trainings.html', {
        'employee': employee,
        'training_records': training_records
    })

@login_required
@permission_required('employees.add_trainingrecord', raise_exception=True)
def training_record_create(request):
    employee_pk = request.GET.get('employee_pk')
    if not employee_pk:
        logger.error('Не указан сотрудник для создания записи об обучении пользователем: %s', request.user.username)
        messages.error(request, 'Пожалуйста, выберите сотрудника.')
        return redirect('employees:employee_list')
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            training_record = form.save(commit=False)
            training_record.employee = employee
            training_record.save()
            logger.info('Создана запись об обучении для %s пользователем: %s', employee, request.user.username)
            return redirect('employees:employee_trainings', pk=employee_pk)
        else:
            logger.warning('Ошибка валидации формы создания записи об обучении: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = TrainingRecordForm()
        logger.debug('Открыта форма создания записи об обучении для сотрудника: %s пользователем: %s', employee, request.user.username)
    return render(request, 'training_record_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Добавить'
    })

@login_required
@permission_required('employees.change_trainingrecord', raise_exception=True)
def training_record_edit(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, instance=training_record)
        if form.is_valid():
            training_record = form.save()
            logger.info('Обновлена запись об обучении для %s пользователем: %s', employee, request.user.username)
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            logger.warning('Ошибка валидации формы редактирования записи об обучении: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = TrainingRecordForm(instance=training_record)
        logger.debug('Открыта форма редактирования записи об обучении: %s пользователем: %s', training_record, request.user.username)
    return render(request, 'training_record_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Редактировать'
    })

@login_required
def training_record_delete(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_trainingrecord'):
            logger.info('Удалена запись об обучении: %s пользователем: %s', training_record, request.user.username)
            training_record.delete()
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:training_record_delete_confirm', pk=pk)
    logger.debug('Открыта страница подтверждения удаления записи об обучении: %s пользователем: %s', training_record, request.user.username)
    return render(request, 'training_record_confirm_delete.html', {
        'training_record': training_record,
        'employee': employee
    })

@login_required
def training_record_delete_confirm(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление записи об обучении: %s пользователем mto', training_record)
            training_record.delete()
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
    return render(request, 'training_record_confirm_delete.html', {
        'training_record': training_record,
        'employee': employee,
        'confirm_mode': True
    })

@login_required
def department_list(request):
    logger.info('Запрошен список подразделений пользователем: %s', request.user.username)
    departments = Department.objects.all()
    return render(request, 'departments.html', {'departments': departments})

@login_required
@permission_required('employees.add_department', raise_exception=True)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            logger.info('Создано подразделение: %s пользователем: %s', department, request.user.username)
            return redirect('employees:department_list')
        else:
            logger.warning('Ошибка валидации формы создания подразделения: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = DepartmentForm()
        logger.debug('Открыта форма создания подразделения пользователем: %s', request.user.username)
    return render(request, 'department_form.html', {'form': form, 'action': 'Добавить'})

@login_required
@permission_required('employees.change_department', raise_exception=True)
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            logger.info('Обновлено подразделение: %s пользователем: %s', department, request.user.username)
            return redirect('employees:department_list')
        else:
            logger.warning('Ошибка валидации формы редактирования подразделения: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = DepartmentForm(instance=department)
        logger.debug('Открыта форма редактирования подразделения: %s пользователем: %s', department, request.user.username)
    return render(request, 'department_form.html', {'form': form, 'action': 'Редактировать'})

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_department'):
            logger.info('Удалено подразделение: %s пользователем: %s', department, request.user.username)
            department.delete()
            return redirect('employees:department_list')
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:department_delete_confirm', pk=pk)
    logger.debug('Открыта страница подтверждения удаления подразделения: %s пользователем: %s', department, request.user.username)
    return render(request, 'department_confirm_delete.html', {'department': department})

@login_required
def department_delete_confirm(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление подразделения: %s пользователем mto', department)
            department.delete()
            return redirect('employees:department_list')
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
    return render(request, 'department_confirm_delete.html', {'department': department, 'confirm_mode': True})

@login_required
def position_list(request):
    logger.info('Запрошен список должностей пользователем: %s', request.user.username)
    positions = Position.objects.all()
    return render(request, 'positions.html', {'positions': positions})

@login_required
@permission_required('employees.add_position', raise_exception=True)
def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            logger.info('Создана должность: %s пользователем: %s', position, request.user.username)
            return redirect('employees:position_list')
        else:
            logger.warning('Ошибка валидации формы создания должности: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = PositionForm()
        logger.debug('Открыта форма создания должности пользователем: %s', request.user.username)
    return render(request, 'position_form.html', {'form': form, 'action': 'Добавить'})

@login_required
@permission_required('employees.change_position', raise_exception=True)
def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
            logger.info('Обновлена должность: %s пользователем: %s', position, request.user.username)
            return redirect('employees:position_list')
        else:
            logger.warning('Ошибка валидации формы редактирования должности: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = PositionForm(instance=position)
        logger.debug('Открыта форма редактирования должности: %s пользователем: %s', position, request.user.username)
    return render(request, 'position_form.html', {'form': form, 'action': 'Редактировать'})

@login_required
def position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_position'):
            logger.info('Удалена должность: %s пользователем: %s', position, request.user.username)
            position.delete()
            return redirect('employees:position_list')
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:position_delete_confirm', pk=pk)
    logger.debug('Открыта страница подтверждения удаления должности: %s пользователем: %s', position, request.user.username)
    return render(request, 'position_confirm_delete.html', {'position': position})

@login_required
def position_delete_confirm(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление должности: %s пользователем mto', position)
            position.delete()
            return redirect('employees:position_list')
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
    return render(request, 'position_confirm_delete.html', {'position': position, 'confirm_mode': True})

@login_required
def training_list(request):
    logger.info('Запрошен список программ обучения пользователем: %s', request.user.username)
    trainings = TrainingProgram.objects.all()
    return render(request, 'trainings.html', {'trainings': trainings})

@login_required
@permission_required('employees.add_trainingprogram', raise_exception=True)
def training_create(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            training = form.save()
            logger.info('Создана программа обучения: %s пользователем: %s', training, request.user.username)
            return redirect('employees:training_list')
        else:
            logger.warning('Ошибка валидации формы создания программы обучения: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = TrainingProgramForm()
        logger.debug('Открыта форма создания программы обучения пользователем: %s', request.user.username)
    return render(request, 'training_form.html', {'form': form, 'action': 'Добавить'})

@login_required
@permission_required('employees.change_trainingprogram', raise_exception=True)
def training_edit(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=training)
        if form.is_valid():
            training = form.save()
            logger.info('Обновлена программа обучения: %s пользователем: %s', training, request.user.username)
            return redirect('employees:training_list')
        else:
            logger.warning('Ошибка валидации формы редактирования программы обучения: %s пользователем: %s', form.errors, request.user.username)
    else:
        form = TrainingProgramForm(instance=training)
        logger.debug('Открыта форма редактирования программы обучения: %s пользователем: %s', training, request.user.username)
    return render(request, 'training_form.html', {'form': form, 'action': 'Редактировать'})

@login_required
def training_delete(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_trainingprogram'):
            logger.info('Удалена программа обучения: %s пользователем: %s', training, request.user.username)
            training.delete()
            return redirect('employees:training_list')
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:training_delete_confirm', pk=pk)
    logger.debug('Открыта страница подтверждения удаления программы обучения: %s пользователем: %s', training, request.user.username)
    return render(request, 'training_confirm_delete.html', {'training': training})

@login_required
def training_delete_confirm(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление программы обучения: %s пользователем mto', training)
            training.delete()
            return redirect('employees:training_list')
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
    return render(request, 'training_confirm_delete.html', {'training': training, 'confirm_mode': True})

@login_required
def reports(request):
    logger.info('Запрошен отчет по обучению пользователем: %s', request.user.username)
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
    return render(request, 'reports.html', {
        'report_data': report_data,
        'training_programs': training_programs,
        'employees': employees
    })