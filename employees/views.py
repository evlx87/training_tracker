from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Department, Position
from .forms import EmployeeForm
from django import forms

# Формы для подразделений и должностей (как было ранее)
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
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

def trainings(request):
    return render(request, 'trainings.html')

def reports(request):
    return render(request, 'reports.html')