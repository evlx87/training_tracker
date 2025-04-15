from django.contrib import admin
from .models import Employee, Department, Position

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'middle_name',
        'birth_date',
        'position',
        'department',
        'is_dismissed',
        'is_on_maternity_leave',
        'is_external_part_time',
    )
    list_filter = ('department', 'position', 'is_dismissed', 'is_on_maternity_leave', 'is_external_part_time')
    search_fields = ('last_name', 'first_name', 'middle_name')
    date_hierarchy = 'birth_date'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)