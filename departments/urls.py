from django.urls import path
from .views import DepartmentListView, DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, \
    DepartmentDeleteConfirmView

app_name = 'departments'

urlpatterns = [
    path('', DepartmentListView.as_view(), name='department_list'),
    path('create/', DepartmentCreateView.as_view(), name='department_create'),
    path('<int:pk>/edit/', DepartmentUpdateView.as_view(), name='department_edit'),
    path( '<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete'),
    path('<int:pk>/delete/confirm/', DepartmentDeleteConfirmView.as_view(), name='department_delete_confirm'),
]
