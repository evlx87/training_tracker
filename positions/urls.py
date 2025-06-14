from django.urls import path
from .views import PositionListView, PositionCreateView, PositionUpdateView, PositionDeleteView

app_name = 'positions'

urlpatterns = [
    path('', PositionListView.as_view(), name='position_list'),
    path('create/', PositionCreateView.as_view(), name='position_create'),
    path('<int:pk>/edit/', PositionUpdateView.as_view(), name='position_edit'),
    path('<int:pk>/delete/',PositionDeleteView.as_view(), name='position_delete'),
]