from django.urls import path
from .views import InstructionListView, InstructionDetailView

app_name = 'instructions'

urlpatterns = [
    path('', InstructionListView.as_view(), name='instruction_list'),
    path('<int:pk>/', InstructionDetailView.as_view(), name='instruction_detail'),
]
