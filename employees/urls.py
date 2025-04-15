from django.urls import path
from . import views

app_name = 'employees'
urlpatterns = [
    path('', views.index, name='index'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    path('trainings/', views.trainings, name='trainings'),
    path('reports/', views.reports, name='reports'),
]