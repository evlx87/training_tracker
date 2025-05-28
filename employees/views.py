import logging
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from .forms import EmployeeForm, DepartmentForm, PositionForm, TrainingProgramForm, TrainingRecordForm
from .models import Employee, Department, Position, TrainingProgram, TrainingRecord
from .services import ReportService

# Настройка логгера
logger = logging.getLogger('employees')


# Декоратор для логирования действий в представлениях
def log_view_action(action, model_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            logger.debug(
                '%s %s пользователем: %s',
                action,
                model_name,
                request.user.username)
            return view_func(view, request, *args, **kwargs)
        return wrapper
    return decorator


# Базовый класс для удаления с подтверждением от группы MTO
class MTOConfirmedDeleteView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        DeleteView):
    confirm_url_name = None  # Должно быть задано в дочернем классе
    permission_required = None  # Должно быть задано в дочернем классе

    def test_func(self):
        return self.request.user.groups.filter(
            name=settings.MTO_GROUP_NAME).exists() or self.request.user.has_perm(
            self.permission_required)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.test_func():
            logger.info(
                'Удален %s: %s пользователем: %s',
                self.model._meta.verbose_name,
                obj,
                request.user.username)
            return super().post(request, *args, **kwargs)
        messages.error(
            request,
            'Удаление требует подтверждения от пользователя из группы MTO.')
        return redirect(self.confirm_url_name, pk=obj.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.path.endswith('confirm/'):
            context['confirm_mode'] = True
        return context


class IndexView(TemplateView):
    template_name = 'index.html'
    @log_view_action('Открыта', 'главная страница')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        return Employee.objects.select_related('position', 'department')

    @log_view_action('Запрошен список', 'сотрудников')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    permission_required = 'employees.add_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        return context

    @log_view_action('Открыта форма создания', 'сотрудника')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        employee = form.save()
        logger.info('Создан сотрудник: %s пользователем: %s',
                    employee, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания сотрудника: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class EmployeeUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    permission_required = 'employees.change_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context

    @log_view_action('Открыта форма редактирования', 'сотрудника')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        employee = form.save()
        logger.info('Обновлен сотрудник: %s пользователем: %s',
                    employee, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования сотрудника: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class EmployeeDeleteView(MTOConfirmedDeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    confirm_url_name = 'employees:employee_delete_confirm'
    permission_required = 'employees.delete_employee'


class EmployeeDeleteConfirmView(MTOConfirmedDeleteView):
    model = Employee
    template_name = 'employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    confirm_url_name = 'employees:employee_delete_confirm'
    permission_required = 'employees.delete_employee'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление сотрудника: %s пользователем из группы MTO', obj)
            return super(
                MTOConfirmedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        return self.render_to_response(self.get_context_data())


class EmployeeTrainingsView(LoginRequiredMixin, TemplateView):
    template_name = 'employee_trainings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, pk=self.kwargs['pk'])
        context['employee'] = employee
        context['trainings'] = employee.training_set.all()  # Получение тренировок сотрудника
        return context

    @log_view_action('Запрошены записи об обучении для', 'сотрудника')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TrainingRecordCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training_record_form.html'
    permission_required = 'employees.add_trainingrecord'

    def get_employee(self):
        """Получает сотрудника из URL или POST-запроса."""
        employee_pk = self.kwargs.get('employee_pk') or self.request.POST.get('employee_pk')
        if employee_pk:
            return get_object_or_404(Employee, pk=employee_pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_employee()
        if employee:
            context['employee'] = employee
        context['action'] = 'Добавить'
        return context

    @log_view_action('Открыта форма создания записи об', 'обучении')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        employee = self.get_employee()
        if not employee:
            logger.error(
                'Не указан сотрудник для создания записи об обучении пользователем: %s',
                self.request.user.username
            )
            form.add_error(None, 'Сотрудник не выбран.')
            return self.form_invalid(form)

        form.instance.employee = employee
        training_record = form.save()
        logger.info(
            'Создана запись об обучении для %s пользователем: %s',
            form.instance.employee,
            self.request.user.username
        )
        return redirect('employees:employee_trainings', pk=form.instance.employee.pk)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания записи об обучении: %s пользователем: %s',
            form.errors,
            self.request.user.username
        )
        return super().form_invalid(form)


class TrainingRecordUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'training_record_form.html'
    permission_required = 'employees.change_trainingrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        context['action'] = 'Редактировать'
        return context

    @log_view_action('Открыта форма редактирования записи об', 'обучении')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        training_record = form.save()
        logger.info(
            'Обновлена запись об обучении для %s пользователем: %s',
            training_record.employee,
            self.request.user.username)
        return redirect(
            'employees:employee_trainings',
            pk=training_record.employee.pk)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования записи об обучении: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class TrainingRecordDeleteView(MTOConfirmedDeleteView):
    model = TrainingRecord
    template_name = 'training_record_confirm_delete.html'
    confirm_url_name = 'employees:training_record_delete_confirm'
    permission_required = 'employees.delete_trainingrecord'

    def get_success_url(self):
        return reverse_lazy(
            'employees:employee_trainings', kwargs={
                'pk': self.get_object().employee.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        return context


class TrainingRecordDeleteConfirmView(MTOConfirmedDeleteView):
    model = TrainingRecord
    template_name = 'training_record_confirm_delete.html'
    confirm_url_name = 'employees:training_record_delete_confirm'
    permission_required = 'employees.delete_trainingrecord'

    def get_success_url(self):
        return reverse_lazy(
            'employees:employee_trainings', kwargs={
                'pk': self.get_object().employee.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.get_object().employee
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление записи об обучении: %s пользователем из группы MTO',
                obj)
            return super(
                MTOConfirmedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        return self.render_to_response(self.get_context_data())


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'departments.html'
    context_object_name = 'departments'
    paginate_by = 20

    @log_view_action('Запрошен список', 'подразделений')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DepartmentCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department_form.html'
    success_url = reverse_lazy('employees:department_list')
    permission_required = 'employees.add_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        return context

    @log_view_action('Открыта форма создания', 'подразделения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        department = form.save()
        logger.info('Создано подразделение: %s пользователем: %s',
                    department, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания подразделения: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class DepartmentUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department_form.html'
    success_url = reverse_lazy('employees:department_list')
    permission_required = 'employees.change_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context

    @log_view_action('Открыта форма редактирования', 'подразделения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        department = form.save()
        logger.info(
            'Обновлено подразделение: %s пользователем: %s',
            department,
            self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования подразделения: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class DepartmentDeleteView(MTOConfirmedDeleteView):
    model = Department
    template_name = 'department_confirm_delete.html'
    success_url = reverse_lazy('employees:department_list')
    confirm_url_name = 'employees:department_delete_confirm'
    permission_required = 'employees.delete_department'


class DepartmentDeleteConfirmView(MTOConfirmedDeleteView):
    model = Department
    template_name = 'department_confirm_delete.html'
    success_url = reverse_lazy('employees:department_list')
    confirm_url_name = 'employees:department_delete_confirm'
    permission_required = 'employees.delete_department'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление подразделения: %s пользователем из группы MTO', obj)
            return super(
                MTOConfirmedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        return self.render_to_response(self.get_context_data())


class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'positions.html'
    context_object_name = 'positions'
    paginate_by = 20

    @log_view_action('Запрошен список', 'должностей')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PositionCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'position_form.html'
    success_url = reverse_lazy('employees:position_list')
    permission_required = 'employees.add_position'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        return context

    @log_view_action('Открыта форма создания', 'должности')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        position = form.save()
        logger.info('Создана должность: %s пользователем: %s',
                    position, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания должности: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class PositionUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'position_form.html'
    success_url = reverse_lazy('employees:position_list')
    permission_required = 'employees.change_position'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context

    @log_view_action('Открыта форма редактирования', 'должности')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        position = form.save()
        logger.info('Обновлена должность: %s пользователем: %s',
                    position, self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования должности: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class PositionDeleteView(MTOConfirmedDeleteView):
    model = Position
    template_name = 'position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')
    confirm_url_name = 'employees:position_delete_confirm'
    permission_required = 'employees.delete_position'


class PositionDeleteConfirmView(MTOConfirmedDeleteView):
    model = Position
    template_name = 'position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')
    confirm_url_name = 'employees:position_delete_confirm'
    permission_required = 'employees.delete_position'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление должности: %s пользователем из группы MTO', obj)
            return super(
                MTOConfirmedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        return self.render_to_response(self.get_context_data())


class TrainingListView(LoginRequiredMixin, ListView):
    model = TrainingProgram
    template_name = 'trainings.html'
    context_object_name = 'trainings'
    paginate_by = 20

    @log_view_action('Запрошен список', 'программ обучения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TrainingCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'training_form.html'
    success_url = reverse_lazy('employees:training_list')
    permission_required = 'employees.add_trainingprogram'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Добавить'
        return context

    @log_view_action('Открыта форма создания', 'программы обучения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        training = form.save()
        logger.info(
            'Создана программа обучения: %s пользователем: %s',
            training,
            self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания программы обучения: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class TrainingUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'training_form.html'
    success_url = reverse_lazy('employees:training_list')
    permission_required = 'employees.change_trainingprogram'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context

    @log_view_action('Открыта форма редактирования', 'программы обучения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        training = form.save()
        logger.info(
            'Обновлена программа обучения: %s пользователем: %s',
            training,
            self.request.user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования программы обучения: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class TrainingDeleteView(MTOConfirmedDeleteView):
    model = TrainingProgram
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('employees:training_list')
    confirm_url_name = 'employees:training_delete_confirm'
    permission_required = 'employees.delete_trainingprogram'


class TrainingDeleteConfirmView(MTOConfirmedDeleteView):
    model = TrainingProgram
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('employees:training_list')
    confirm_url_name = 'employees:training_delete_confirm'
    permission_required = 'employees.delete_trainingprogram'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление программы обучения: %s пользователем из группы MTO',
                obj)
            return super(
                MTOConfirmedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        return self.render_to_response(self.get_context_data())


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_data, training_programs = ReportService.generate_training_report()
        context['report_data'] = report_data
        context['training_programs'] = training_programs
        return context

    @log_view_action('Запрошен', 'отчет по обучению')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
