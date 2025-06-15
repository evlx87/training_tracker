import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from employees.views import log_view_action, EditorModeratedDeleteView
from .forms import DepartmentForm
from .models import Department

logger = logging.getLogger('departments')


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'departments/department_list.html'
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
    template_name = 'departments/department_form.html'
    success_url = reverse_lazy('departments:department_list')
    permission_required = 'departments.add_department'

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
    template_name = 'departments/department_form.html'
    success_url = reverse_lazy('departments:department_list')
    permission_required = 'departments.change_department'

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


class DepartmentDeleteView(EditorModeratedDeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('departments:department_list')
    confirm_url_name = 'departments:department_delete_confirm'
    permission_required = 'departments.delete_department'


class DepartmentDeleteConfirmView(EditorModeratedDeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('departments:department_list')
    confirm_url_name = 'departments:department_delete_confirm'
    permission_required = 'departments.delete_department'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.username
        if request.user.groups.filter(name=settings.MODERATOR_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление подразделения: %s пользователем из группы модераторов: %s',
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
            'Отказано в подтверждении удаления подразделения: %s пользователем: %s',
            obj,
            user)
        return self.render_to_response(self.get_context_data())
