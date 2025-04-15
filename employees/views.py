from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Department, Position
from django import forms

# Create your views here.
def index(request):
    return render(request, 'index.html')


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})


# Представления для подразделений
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
    if Employee.objects.filter(department=department).exists():
        return render(request, 'department_confirm_delete.html', {
            'department': department,
            'error': 'Нельзя удалить подразделение, так как оно связано с сотрудниками.'
        })
    if request.method == 'POST':
        department.delete()
        return redirect('employees:department_list')
    return render(request, 'department_confirm_delete.html', {'department': department})

# Представления для должностей
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

# Форма для подразделений
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
        }

# Форма для должностей
class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
        }