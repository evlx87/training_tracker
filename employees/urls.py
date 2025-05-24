from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('employees/<int:pk>/delete/confirm/', views.EmployeeDeleteConfirmView.as_view(), name='employee_delete_confirm'),
    path('employees/<int:pk>/trainings/', views.EmployeeTrainingsView.as_view(), name='employee_trainings'),
    path('training-records/create/<int:employee_pk>/', views.TrainingRecordCreateView.as_view(), name='training_record_create'),
    path('trainings-records/<int:pk>/edit/', views.TrainingRecordUpdateView.as_view(), name='training_record_edit'),
    path('trainings-records/<int:pk>/delete/', views.TrainingRecordDeleteView.as_view(), name='training_record_delete'),
    path('trainings-records/<int:pk>/delete/confirm/', views.TrainingRecordDeleteConfirmView.as_view(), name='training_record_delete_confirm'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    path('departments/<int:pk>/delete/confirm/', views.DepartmentDeleteConfirmView.as_view(), name='department_delete_confirm'),
    path('positions/', views.PositionListView.as_view(), name='position_list'),
    path('positions/create/', views.PositionCreateView.as_view(), name='position_create'),
    path('positions/<int:pk>/edit/', views.PositionUpdateView.as_view(), name='position_edit'),
    path('positions/<int:pk>/delete/', views.PositionDeleteView.as_view(), name='position_delete'),
    path('positions/<int:pk>/delete/confirm/', views.PositionDeleteConfirmView.as_view(), name='position_delete_confirm'),
    path('trainings/', views.TrainingListView.as_view(), name='training_list'),
    path('trainings/create/', views.TrainingCreateView.as_view(), name='training_create'),
    path('trainings/<int:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_edit'),
    path('trainings/<int:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),
    path('trainings/<int:pk>/delete/confirm/', views.TrainingDeleteConfirmView.as_view(), name='training_delete_confirm'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
]