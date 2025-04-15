from django.urls import path

from employees.views import employee_list, index, departments, trainings, reports

app_name = 'employees'

urlpatterns = [
    path('', index, name='index'),
    path('employees/', employee_list, name='employee_list'),
    path('departments/', departments, name='departments'),
    path('trainings/', trainings, name='trainings'),
    path('reports/', reports, name='reports'),
]