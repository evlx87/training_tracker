from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.index, name='index'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/delete/confirm/', views.employee_delete_confirm, name='employee_delete_confirm'),
    path('employees/<int:pk>/trainings/', views.employee_trainings, name='employee_trainings'),
    path('trainings-records/create/', views.training_record_create, name='training_record_create'),
    path('trainings-records/<int:pk>/edit/', views.training_record_edit, name='training_record_edit'),
    path('trainings-records/<int:pk>/delete/', views.training_record_delete, name='training_record_delete'),
    path('trainings-records/<int:pk>/delete/confirm/', views.training_record_delete_confirm, name='training_record_delete_confirm'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('departments/<int:pk>/delete/confirm/', views.department_delete_confirm, name='department_delete_confirm'),
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    path('positions/<int:pk>/delete/confirm/', views.position_delete_confirm, name='position_delete_confirm'),
    path('trainings/', views.training_list, name='training_list'),
    path('trainings/create/', views.training_create, name='training_create'),
    path('trainings/<int:pk>/edit/', views.training_edit, name='training_edit'),
    path('trainings/<int:pk>/delete/', views.training_delete, name='training_delete'),
    path('trainings/<int:pk>/delete/confirm/', views.training_delete_confirm, name='training_delete_confirm'),
    path('reports/', views.reports, name='reports'),
]