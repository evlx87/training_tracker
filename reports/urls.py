from django.urls import path
from .views import ReportsView, ExportReportView

app_name = 'reports'

urlpatterns = [
    path('', ReportsView.as_view(), name='report_list'),
    path('export/', ExportReportView.as_view(), name='export_report'),
]