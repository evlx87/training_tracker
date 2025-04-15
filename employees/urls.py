from django.urls import path

from employees.views import employee_list

app_name = 'employees'

urlpatterns = [
    path('/', employee_list, name='employee_list'),
]