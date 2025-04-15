from django.shortcuts import render
from .models import Employee


# Create your views here.
def index(request):
    return render(request, 'index.html')


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee_list.html', {'employees': employees})


def departments(request):
    return render(request, 'departments.html')


def trainings(request):
    return render(request, 'trainings.html')


def reports(request):
    return render(request, 'reports.html')