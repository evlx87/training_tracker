from django.forms import ModelForm, TextInput, Textarea
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Добавляем messages
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord
from .forms import EmployeeForm, DepartmentForm, PositionForm, TrainingProgramForm, TrainingRecordForm
from django.utils import timezone
from datetime import timedelta


# Формы
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


# Представления
def index(request):
    return render(request, 'index.html')


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})


def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_form.html', {'form': form, 'action': 'Добавить'})


def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Редактировать'})


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employees:employee_list')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})


def employee_trainings(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    training_records = TrainingRecord.objects.filter(employee=employee)
    return render(request, 'employee_trainings.html', {
        'employee': employee,
        'training_records': training_records
    })


def training_record_create(request):
    employee_pk = request.GET.get('employee_pk')
    if not employee_pk:
        messages.error(request, 'Пожалуйста, выберите сотрудника.')  # Добавляем сообщение об ошибке
        return redirect('employees:employee_list')
    employee = get_object_or_404(Employee, pk=employee_pk)
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            training_record = form.save(commit=False)
            training_record.employee = employee
            training_record.save()
            return redirect('employees:employee_trainings', pk=employee_pk)
    else:
        form = TrainingRecordForm()
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
            form.save()
            return redirect('employees:employee_trainings', pk=employee.pk)
    else:
        form = TrainingRecordForm(instance=training_record)
    return render(request, 'training_record_form.html', {
        'form': form,
        'employee': employee,
        'action': 'Редактировать'
    })


def training_record_delete(request, pk):
    training_record = get_object_or_404(TrainingRecord, pk=pk)
    employee = training_record.employee
    if request.method == 'POST':
        training_record.delete()
        return redirect('employees:employee_trainings', pk=employee.pk)
    return render(request, 'training_record_confirm_delete.html', {
        'training_record': training_record,
        'employee': employee
    })


def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments.html', {'departments': departments})


def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employees:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form, 'action': 'Добавить'})


def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('employees:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form, 'action': 'Редактировать'})


def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('employees:department_list')
    return render(request, 'department_confirm_delete.html', {'department': department})


def position_list(request):
    positions = Position.objects.all()
    return render(request, 'positions.html', {'positions': positions})


def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employees:position_list')
    else:
        form = PositionForm()
    return render(request, 'position_form.html', {'form': form, 'action': 'Добавить'})


def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            return redirect('employees:position_list')
    else:
        form = PositionForm(instance=position)
    return render(request, 'position_form.html', {'form': form, 'action': 'Редактировать'})


def position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        position.delete()
        return redirect('employees:position_list')
    return render(request, 'position_confirm_delete.html', {'position': position})


def training_list(request):
    trainings = TrainingProgram.objects.all()
    return render(request, 'trainings.html', {'trainings': trainings})


def training_create(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employees:training_list')
    else:
        form = TrainingProgramForm()
    return render(request, 'training_form.html', {'form': form, 'action': 'Добавить'})


def training_edit(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            return redirect('employees:training_list')
    else:
        form = TrainingProgramForm(instance=training)
    return render(request, 'training_form.html', {'form': form, 'action': 'Редактировать'})


def training_delete(request, pk):
    training = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        training.delete()
        return redirect('employees:training_list')
    return render(request, 'training_confirm_delete.html', {'training': training})


def reports(request):
    employees = Employee.objects.select_related('position', 'department').all()
    training_programs = TrainingProgram.objects.all()
    today = timezone.now().date()
    six_months = timedelta(days=180)  # Примерно 6 месяцев

    report_data = []
    for employee in employees:
        employee_data = {
            'employee': employee,
            'trainings': {}  # Теперь словарь вместо списка
        }
        for program in training_programs:
            # Находим последнюю запись об обучении
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
                    due_date = latest_record.completion_date + timedelta(days=program.recurrence_period * 365)
                    warning_date = due_date - six_months
                    if today > due_date:
                        status['class'] = 'overdue'
                    elif today >= warning_date:
                        status['class'] = 'warning'

            # Используем program.id как ключ в словаре trainings
            employee_data['trainings'][program.id] = status

        report_data.append(employee_data)

    return render(request, 'reports.html', {
        'report_data': report_data,
        'training_programs': training_programs,
        'employees': employees
    })