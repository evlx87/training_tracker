import logging
from datetime import datetime
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView

from employees.models import DeletionRequest
from .forms import EmployeeForm, TrainingRecordForm
from .models import Employee, TrainingRecord

# Настройка логгера
logger = logging.getLogger('employees')


# Декоратор для логирования действий в представлениях
def log_view_action(action, model_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            logger.info(
                '%s %s пользователем: %s, метод: %s, путь: %s, параметры: %s',
                action,
                model_name,
                user,
                request.method,
                request.path,
                request.GET.dict() if request.method == 'GET' else request.POST.dict())
            try:
                response = view_func(view, request, *args, **kwargs)
                logger.debug(
                    'Успешное выполнение %s %s пользователем: %s',
                    action,
                    model_name,
                    user)
                return response
            except Exception as e:
                logger.error(
                    'Ошибка при %s %s пользователем: %s, ошибка: %s',
                    action, model_name, user, str(e), exc_info=True
                )
                raise
        return wrapper
    return decorator


class EditorModeratedDeleteView(PermissionRequiredMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        content_type = ContentType.objects.get_for_model(self.model)

        # Проверяем, есть ли существующий запрос на удаление
        existing_request = DeletionRequest.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
            status=DeletionRequest.STATUS_PENDING
        ).first()

        if existing_request:
            messages.warning(
                request, 'Запрос на удаление уже существует и ожидает подтверждения.')
            logger.warning(
                'Попытка повторного создания запроса на удаление %s пользователем: %s',
                obj, user.username
            )
            return redirect(self.success_url)

        # Если пользователь в группе Moderators, он может удалять напрямую
        if user.groups.filter(name='Moderators').exists():
            return super().get(request, *args, **kwargs)

        # Если пользователь в группе Editors, создаем запрос на удаление
        if user.groups.filter(name='Editors').exists():
            DeletionRequest.objects.create(
                content_type=content_type,
                object_id=obj.pk,
                created_by=user
            )
            messages.success(
                request, 'Запрос на удаление отправлен. Ожидайте подтверждения от модератора.')
            logger.info(
                'Создан запрос на удаление %s пользователем: %s',
                obj, user.username
            )
            return redirect(self.success_url)

        messages.error(request, 'У вас нет прав для выполнения этой операции.')
        logger.warning(
            'Отказано в удалении %s пользователем: %s (нет прав)',
            obj, user.username
        )
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user

        # Только Moderators могут подтверждать удаление
        if user.groups.filter(name='Moderators').exists():
            content_type = ContentType.objects.get_for_model(self.model)
            deletion_request = DeletionRequest.objects.filter(
                content_type=content_type,
                object_id=obj.pk,
                status=DeletionRequest.STATUS_PENDING
            ).first()

            if deletion_request:
                deletion_request.status = DeletionRequest.STATUS_APPROVED
                deletion_request.reviewed_by = user
                deletion_request.reviewed_at = datetime.now()
                deletion_request.save()
                logger.info(
                    'Подтверждено удаление %s пользователем из группы Moderators: %s',
                    obj, user.username
                )
                return super().post(request, *args, **kwargs)

            messages.error(request, 'Запрос на удаление не найден.')
            logger.warning(
                'Не найден запрос на удаление %s для подтверждения пользователем: %s',
                obj, user.username
            )
            return redirect(self.success_url)

        messages.error(
            request,
            'Только пользователь из группы Moderators может подтвердить удаление.')
        logger.warning(
            'Отказано в подтверждении удаления %s пользователем: %s',
            obj, user.username
        )
        return redirect(self.success_url)


class DeletionRequestListView(LoginRequiredMixin, ListView):
    model = DeletionRequest
    template_name = 'deletion_requests.html'
    context_object_name = 'deletion_requests'
    paginate_by = 20

    def get_queryset(self):
        return DeletionRequest.objects.filter(
            status=DeletionRequest.STATUS_PENDING).select_related('created_by', 'reviewed_by')

    @log_view_action('Запрошен список', 'запросов на удаление')
    def get(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Moderators').exists():
            messages.error(
                request,
                'Только пользователи группы Moderators могут просматривать запросы на удаление.')
            logger.warning(
                'Отказано в доступе к списку запросов на удаление пользователю: %s',
                request.user.username)
            return redirect('index')
        return super().get(request, *args, **kwargs)


class DeletionRequestConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'deletion_request_confirm.html'
    success_url = reverse_lazy('employees:deletion_request_list')

    def get_object(self):
        try:
            return DeletionRequest.objects.get(pk=self.kwargs['pk'])
        except DeletionRequest.DoesNotExist:
            messages.error(self.request, 'Запрос на удаление не найден.')
            logger.warning('Запрос на удаление #%s не найден.', self.kwargs['pk'])
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        deletion_request = self.get_object()
        if not deletion_request:
            return self.redirect_to_success()

        if not request.user.groups.filter(name='Moderators').exists():
            messages.error(request, 'Только модераторы могут обрабатывать запросы на удаление.')
            logger.warning('Отказано в обработке запроса на удаление #%s пользователю: %s',
                           deletion_request.pk, request.user.username)
            return self.redirect_to_success()

        action = request.POST.get('confirm')
        if action == 'approve':
            deletion_request.status = DeletionRequest.STATUS_APPROVED
            deletion_request.reviewed_by = request.user
            deletion_request.reviewed_at = timezone.now()
            deletion_request.save()
            try:
                if deletion_request.content_object:
                    deletion_request.content_object.delete()
                    logger.info('Объект %s удалён для запроса #%s.',
                                deletion_request.content_object, deletion_request.pk)
                else:
                    logger.warning('Объект для удаления в запросе #%s уже отсутствует.',
                                   deletion_request.pk)
            except Exception as e:
                logger.error('Ошибка при удалении объекта для запроса #%s: %s',
                             deletion_request.pk, str(e))
            messages.success(request, 'Запрос на удаление одобрен.')
            logger.info('Запрос на удаление #%s одобрен пользователем: %s',
                        deletion_request.pk, request.user.username)
        elif action == 'reject':
            deletion_request.status = DeletionRequest.STATUS_REJECTED
            deletion_request.reviewed_by = request.user
            deletion_request.reviewed_at = timezone.now()
            deletion_request.save()
            messages.success(request, 'Запрос на удаление отклонён.')
            logger.info('Запрос на удаление #%s отклонён пользователем: %s',
                        deletion_request.pk, request.user.username)

        return self.redirect_to_success()

    def redirect_to_success(self):
        return redirect(self.success_url)


class IndexView(TemplateView):
    template_name = 'index.html'

    @log_view_action('Открыта', 'главная страница')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Поиск по фамилии
        search_last_name = self.request.GET.get('search_last_name', '').strip()
        if search_last_name:
            queryset = queryset.filter(last_name__istartswith=search_last_name)

        # Сортировка
        sort_by = self.request.GET.get('sort_by', 'last_name')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by == 'last_name':
            if sort_order == 'desc':
                queryset = queryset.order_by('-last_name', '-first_name', '-middle_name')
            else:
                queryset = queryset.order_by('last_name', 'first_name', 'middle_name')
        # Добавьте другие поля для сортировки, если нужно
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_last_name'] = self.request.GET.get('search_last_name', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'last_name')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')
        return context

    @log_view_action('Запрошен список', 'сотрудников')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmployeeCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
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
            form.errors, self.request.user.username
        )
        return super().form_invalid(form)


class EmployeeUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
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


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Editors').exists():
            logger.warning(f"Попытка удаления сотрудника {self.get_object()} пользователем {request.user} без прав Editors")
            messages.error(request, 'У вас нет прав для инициирования удаления.')
            return redirect('employees:employee_list')
        logger.debug(f"Пользователь {request.user} инициирует удаление сотрудника {self.get_object()}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Проверяем, есть ли существующий запрос на удаление
        obj = self.get_object()
        content_type = ContentType.objects.get_for_model(self.model)
        existing_request = DeletionRequest.objects.filter(
            content_type=content_type,
            object_id=obj.pk,
            status=DeletionRequest.STATUS_PENDING
        ).first()
        if existing_request:
            messages.warning(request, 'Запрос на удаление уже существует и ожидает подтверждения.')
            logger.warning(f"Попытка повторного создания запроса на удаление {obj} пользователем: {request.user}")
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Создаём запрос на удаление
        DeletionRequest.objects.create(
            content_type=ContentType.objects.get_for_model(self.model),
            object_id=self.get_object().pk,
            created_by=self.request.user,
            status=DeletionRequest.STATUS_PENDING
        )
        messages.success(self.request, 'Запрос на удаление сотрудника успешно отправлен.')
        logger.info(f"Создан запрос на удаление сотрудника {self.get_object()} пользователем {self.request.user}")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Подтверждение запроса на удаление'
        context['employee'] = self.get_object()  # Для совместимости с шаблоном
        return context


class EmployeeDeleteConfirmView(EditorModeratedDeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    confirm_url_name = 'employees:employee_delete_confirm'
    permission_required = 'employees.delete_employee'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.username
        if request.user.groups.filter(name=settings.MODERATOR_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление сотрудника: %s пользователем из группы MTO: %s',
                obj,
                user)
            return super(
                EditorModeratedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        logger.warning(
            'Отказано в подтверждении удаления сотрудника: %s пользователем: %s',
            obj,
            user)
        return self.render_to_response(self.get_context_data())


class EmployeeTrainingsView(LoginRequiredMixin, TemplateView):
    template_name = 'employees/employee_trainings.html'
    context_object_name = 'training_records'
    permission_required = 'employees.view_employee'

    def get_context_data(self, **kwargs):
        logger.debug(
            "Вызван get_context_data в EmployeeTrainingsView для pk=%s пользователем: %s",
            self.kwargs['pk'],
            self.request.user.username)
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, pk=self.kwargs['pk'])
        context['employee'] = employee
        trainings = employee.trainingrecord_set.all()
        context['training_records'] = trainings
        logger.debug(
            "Найдено %d записей об обучении для сотрудника %s",
            trainings.count(),
            employee)
        return context

    @log_view_action('Запрошены записи об обучении для', 'сотрудника')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TrainingRecordCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'trainings/training_record_form.html'
    permission_required = 'employees.add_trainingrecord'

    def get_employee(self):
        employee_pk = self.kwargs.get(
            'employee_pk') or self.request.POST.get('employee_pk')
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
        user = self.request.user.username
        if not employee:
            logger.error(
                'Не указан сотрудник для создания записи об обучении пользователем: %s',
                user)
            form.add_error(None, 'Сотрудник не выбран.')
            return self.form_invalid(form)
        form.instance.employee = employee
        training_record = form.save()
        logger.info(
            'Создана запись об обучении для %s пользователем: %s',
            training_record.employee,
            user)
        return redirect(
            'employees:employee_trainings',
            pk=training_record.employee.pk)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы создания записи об обучении: %s пользователем: %s',
            form.errors,
            self.request.user.username)
        return super().form_invalid(form)


class TrainingRecordUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TrainingRecord
    form_class = TrainingRecordForm
    template_name = 'trainings/training_record_form.html'
    permission_required = 'employees.change_trainingrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_pk = self.request.GET.get('employee_pk')
        if employee_pk:
            context['employee'] = Employee.objects.get(pk=employee_pk)
        else:
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
            training_record.employee, self.request.user.username
        )
        return redirect('employees:employee_trainings', employee_pk=training_record.employee.pk)

    def form_invalid(self, form):
        logger.warning(
            'Ошибка валидации формы редактирования записи об обучении: %s пользователем: %s',
            form.errors, self.request.user.username)
        return super().form_invalid(form)


class TrainingRecordDeleteView(EditorModeratedDeleteView):
    model = TrainingRecord
    template_name = 'trainings/training_record_confirm_delete.html'
    confirm_url_name = 'employees:training_record_delete_confirm'
    permission_required = 'employees.delete_trainingrecord'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_pk = self.request.GET.get('employee_pk')
        if employee_pk:
            context['employee'] = Employee.objects.get(pk=employee_pk)
        else:
            context['employee'] = self.get_object().employee
        return context

    def get_success_url(self):
        employee_pk = self.request.GET.get('employee_pk')
        if employee_pk:
            return reverse_lazy('employees:employee_trainings', kwargs={'employee_pk': employee_pk})
        return reverse_lazy('employees:employee_trainings', kwargs={'employee_pk': self.get_object().employee.pk})


class TrainingRecordDeleteConfirmView(EditorModeratedDeleteView):
    model = TrainingRecord
    template_name = 'trainings/training_record_confirm_delete.html'
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
        user = request.user.username
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление записи об обучении: %s пользователем из группы MTO: %s',
                obj,
                user)
            return super(
                EditorModeratedDeleteView,
                self).post(
                request,
                *
                args,
                **kwargs)
        messages.error(
            request,
            'Только пользователь из группы MTO может подтвердить удаление.')
        logger.warning(
            'Отказано в подтверждении удаления записи об обучении: %s пользователем: %s',
            obj,
            user)
        return self.render_to_response(self.get_context_data())


class PasswordChangeCustomView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'auth/password_change_form.html'
    success_url = reverse_lazy('employees:password_change_done')

    @log_view_action('Открыта форма смены пароля', 'пользователя')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user.username
        logger.info('Пароль успешно изменен для пользователя: %s', user)
        messages.success(self.request, 'Ваш пароль успешно изменен.')
        return super().form_valid(form)

    def form_invalid(self, form):
        user = self.request.user.username
        logger.warning(
            'Ошибка валидации формы смены пароля для пользователя: %s, ошибки: %s',
            user,
            form.errors)
        return super().form_invalid(form)


class PasswordChangeDoneCustomView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'auth/password_change_done.html'

    @log_view_action('Открыта страница подтверждения смены пароля',
                     'пользователя')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
