from django.urls import path
from .views import TrainingProgramListView, TrainingProgramCreateView, TrainingProgramUpdateView, \
    TrainingProgramDeleteView

app_name = 'trainings'

urlpatterns = [
    path('', TrainingProgramListView.as_view(), name='training_list'),
    path('create/', TrainingProgramCreateView.as_view(), name='training_create'),
    path('<int:pk>/edit/', TrainingProgramUpdateView.as_view(), name='training_edit'),
    path('<int:pk>/delete/', TrainingProgramDeleteView.as_view(), name='training_delete'),
]