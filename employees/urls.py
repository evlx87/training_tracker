from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='employee_list'),
    path('create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('<int:pk>/trainings/', views.EmployeeTrainingsView.as_view(), name='employee_trainings'),

    path('training-records/create/<int:employee_pk>/', views.TrainingRecordCreateView.as_view(), name='training_record_create'),
    path('training-records/<int:pk>/edit/', views.TrainingRecordUpdateView.as_view(), name='training_record_edit'),
    path('training-records/<int:pk>/delete/', views.TrainingRecordDeleteView.as_view(), name='training_record_delete'),

    path('password-change/', views.PasswordChangeCustomView.as_view(), name='password_change'),
    path('password-change/done/', views.PasswordChangeDoneCustomView.as_view(), name='password_change_done'),

    path('deletion-requests/<int:pk>/confirm/', views.DeletionRequestConfirmView.as_view(), name='deletion_request_confirm'),
    path('deletion-requests/', views.DeletionRequestListView.as_view(), name='deletion_request_list'),
]
