from django.contrib import admin
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord


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

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'recurrence_period')
    search_fields = ('name',)

@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'training_program', 'completion_date')
    list_filter = ('training_program', 'completion_date')
    search_fields = ('employee__last_name', 'employee__first_name', 'training_program__name')
    date_hierarchy = 'completion_date'