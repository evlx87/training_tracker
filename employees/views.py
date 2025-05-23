import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from .forms import EmployeeForm, DepartmentForm, PositionForm, TrainingProgramForm, TrainingRecordForm
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord
from .services import ReportService

# Настройка логгера
logger = logging.getLogger('employees')

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        logger.info('Открыта главная страница пользователем: %s', request.user.username)
        return super().get(request, *args, **kwargs)

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'

    def get(self, request, *args, **kwargs):
        logger.info('Запрошен список сотрудников пользователем: %s', request.user.username)
        return super().get(request, *args, **kwargs)

class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    permission_required = 'employees.add_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        logger.debug('Открыта форма создания сотрудника пользователем: %s', self.request.user.username)
        return context

    def form_valid(self, form):
        employee = form.save()
        logger.info('Создан сотрудник: %s пользователем: %s', employee, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы создания сотрудника: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    permission_required = 'employees.change_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        logger.debug('Открыта форма редактирования сотрудника: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def form_valid(self, form):
        employee = form.save()
        logger.info('Обновлен сотрудник: %s пользователем: %s', employee, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы редактирования сотрудника: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def get(self, request, *args, **kwargs):
        logger.debug('Открыта страница подтверждения удаления сотрудника: %s пользователем: %s', self.get_object(), request.user.username)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        employee = self.get_object()
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_employee'):
            logger.info('Удален сотрудник: %s пользователем: %s', employee, request.user.username)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:employee_delete_confirm', pk=employee.pk)

class EmployeeDeleteConfirmView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_mode'] = True
        return context

    def post(self, request, *args, **kwargs):
        employee = self.get_object()
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление сотрудника: %s пользователем mto', employee)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
            return self.render_to_response(self.get_context_data())

class EmployeeTrainingsView(LoginRequiredMixin, TemplateView):
    template_name = 'employee_trainings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, pk=self.kwargs['pk'])
        training_records = TrainingRecord.objects.filter(employee=employee)
        context['employee'] = employee
        context['training_records'] = training_records
        logger.info('Запрошены записи об обучении для сотрудника: %s пользователем: %s', employee, self.request.user.username)
        return context

class TrainingRecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training_record_form.html'
    permission_required = 'employees.add_trainingrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, pk=self.request.GET.get('employee_pk'))
        context['employee'] = employee
        context['action'] = 'Добавить'
        logger.debug('Открыта форма создания записи об обучении для сотрудника: %s пользователем: %s', employee, self.request.user.username)
        return context

    def form_valid(self, form):
        employee = get_object_or_404(Employee, pk=self.request.GET.get('employee_pk'))
        if not employee:
            logger.error('Не указан сотрудник для создания записи об обучении пользователем: %s', self.request.user.username)
            messages.error(self.request, 'Пожалуйста, выберите сотрудника.')
            return redirect('employees:employee_list')
        form.instance.employee = employee
        training_record = form.save()
        logger.info('Создана запись об обучении для %s пользователем: %s', employee, self.request.user.username)
        return redirect('employees:employee_trainings', pk=employee.pk)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы создания записи об обучении: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if not request.GET.get('employee_pk'):
            logger.error('Не указан сотрудник для создания записи об обучении пользователем: %s', request.user.username)
            messages.error(request, 'Пожалуйста, выберите сотрудника.')
            return redirect('employees:employee_list')
        return super().get(request, *args, **kwargs)

class TrainingRecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training_record_form.html'
    permission_required = 'employees.change_trainingrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        context['action'] = 'Редактировать'
        logger.debug('Открыта форма редактирования записи об обучении: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def form_valid(self, form):
        training_record = form.save()
        logger.info('Обновлена запись об обучении для %s пользователем: %s', training_record.employee, self.request.user.username)
        return redirect('employees:employee_trainings', pk=training_record.employee.pk)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы редактирования записи об обучении: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class TrainingRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingRecord
    template_name = 'training_record_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        logger.debug('Открыта страница подтверждения удаления записи об обучении: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def post(self, request, *args, **kwargs):
        training_record = self.get_object()
        employee = training_record.employee
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_trainingrecord'):
            logger.info('Удалена запись об обучении: %s пользователем: %s', training_record, request.user.username)
            training_record.delete()
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:training_record_delete_confirm', pk=training_record.pk)

class TrainingRecordDeleteConfirmView(LoginRequiredMixin, DeleteView):
    model = TrainingRecord
    template_name = 'training_record_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        context['confirm_mode'] = True
        return context

    def post(self, request, *args, **kwargs):
        training_record = self.get_object()
        employee = training_record.employee
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление записи об обучении: %s пользователем mto', training_record)
            training_record.delete()
            return redirect('employees:employee_trainings', pk=employee.pk)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
            return self.render_to_response(self.get_context_data())

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'departments.html'
    context_object_name = 'departments'

    def get(self, request, *args, **kwargs):
        logger.info('Запрошен список подразделений пользователем: %s', request.user.username)
        return super().get(request, *args, **kwargs)

class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department_form.html'
    success_url = reverse_lazy('employees:department_list')
    permission_required = 'employees.add_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        logger.debug('Открыта форма создания подразделения пользователем: %s', self.request.user.username)
        return context

    def form_valid(self, form):
        department = form.save()
        logger.info('Создано подразделение: %s пользователем: %s', department, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы создания подразделения: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department_form.html'
    success_url = reverse_lazy('employees:department_list')
    permission_required = 'employees.change_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        logger.debug('Открыта форма редактирования подразделения: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def form_valid(self, form):
        department = form.save()
        logger.info('Обновлено подразделение: %s пользователем: %s', department, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы редактирования подразделения: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'department_confirm_delete.html'
    success_url = reverse_lazy('employees:department_list')

    def get(self, request, *args, **kwargs):
        logger.debug('Открыта страница подтверждения удаления подразделения: %s пользователем: %s', self.get_object(), request.user.username)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        department = self.get_object()
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_department'):
            logger.info('Удалено подразделение: %s пользователем: %s', department, request.user.username)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:department_delete_confirm', pk=department.pk)

class DepartmentDeleteConfirmView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'department_confirm_delete.html'
    success_url = reverse_lazy('employees:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_mode'] = True
        return context

    def post(self, request, *args, **kwargs):
        department = self.get_object()
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление подразделения: %s пользователем mto', department)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
            return self.render_to_response(self.get_context_data())

class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'positions.html'
    context_object_name = 'positions'

    def get(self, request, *args, **kwargs):
        logger.info('Запрошен список должностей пользователем: %s', request.user.username)
        return super().get(request, *args, **kwargs)

class PositionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'position_form.html'
    success_url = reverse_lazy('employees:position_list')
    permission_required = 'employees.add_position'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        logger.debug('Открыта форма создания должности пользователем: %s', self.request.user.username)
        return context

    def form_valid(self, form):
        position = form.save()
        logger.info('Создана должность: %s пользователем: %s', position, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы создания должности: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class PositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'position_form.html'
    success_url = reverse_lazy('employees:position_list')
    permission_required = 'employees.change_position'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        logger.debug('Открыта форма редактирования должности: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def form_valid(self, form):
        position = form.save()
        logger.info('Обновлена должность: %s пользователем: %s', position, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы редактирования должности: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')

    def get(self, request, *args, **kwargs):
        logger.debug('Открыта страница подтверждения удаления должности: %s пользователем: %s', self.get_object(), self.request.user.username)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        position = self.get_object()
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_position'):
            logger.info('Удалена должность: %s пользователем: %s', position, request.user.username)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:position_delete_confirm', pk=position.pk)

class PositionDeleteConfirmView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_mode'] = True
        return context

    def post(self, request, *args, **kwargs):
        position = self.get_object()
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление должности: %s пользователем mto', position)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
            return self.render_to_response(self.get_context_data())

class TrainingListView(LoginRequiredMixin, ListView):
    model = TrainingProgram
    template_name = 'trainings.html'
    context_object_name = 'trainings'

    def get(self, request, *args, **kwargs):
        logger.info('Запрошен список программ обучения пользователем: %s', request.user.username)
        return super().get(request, *args, **kwargs)

class TrainingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'training_form.html'
    success_url = reverse_lazy('employees:training_list')
    permission_required = 'employees.add_trainingprogram'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        logger.debug('Открыта форма создания программы обучения пользователем: %s', self.request.user.username)
        return context

    def form_valid(self, form):
        training = form.save()
        logger.info('Создана программа обучения: %s пользователем: %s', training, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы создания программы обучения: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class TrainingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'training_form.html'
    success_url = reverse_lazy('employees:training_list')
    permission_required = 'employees.change_trainingprogram'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        logger.debug('Открыта форма редактирования программы обучения: %s пользователем: %s', self.get_object(), self.request.user.username)
        return context

    def form_valid(self, form):
        training = form.save()
        logger.info('Обновлена программа обучения: %s пользователем: %s', training, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning('Ошибка валидации формы редактирования программы обучения: %s пользователем: %s', form.errors, self.request.user.username)
        return super().form_invalid(form)

class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingProgram
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('employees:training_list')

    def get(self, request, *args, **kwargs):
        logger.debug('Открыта страница подтверждения удаления программы обучения: %s пользователем: %s', self.get_object(), request.user.username)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        training = self.get_object()
        if request.user.username == 'mto' or request.user.has_perm('employees.delete_trainingprogram'):
            logger.info('Удалена программа обучения: %s пользователем: %s', training, request.user.username)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Удаление требует подтверждения от пользователя mto.')
            return redirect('employees:training_delete_confirm', pk=training.pk)

class TrainingDeleteConfirmView(LoginRequiredMixin, DeleteView):
    model = TrainingProgram
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('employees:training_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_mode'] = True
        return context

    def post(self, request, *args, **kwargs):
        training = self.get_object()
        if request.user.username == 'mto':
            logger.info('Подтверждено удаление программы обучения: %s пользователем mto', training)
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request, 'Только пользователь mto может подтвердить удаление.')
            return self.render_to_response(self.get_context_data())

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_data, training_programs = ReportService.generate_training_report()
        context['report_data'] = report_data
        context['training_programs'] = training_programs
        context['employees'] = Employee.objects.all()
        logger.info('Запрошен отчет по обучению пользователем: %s', self.request.user.username)
        return context
