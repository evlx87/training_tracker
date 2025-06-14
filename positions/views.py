import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from employees.views import log_view_action, EditorModeratedDeleteView
from .forms import PositionForm
from .models import Position

logger = logging.getLogger('positions')


class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'positions/position_list.html'
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
    template_name = 'positions/position_form.html'
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
            form.errors, self.request.user.username
        )
        return super().form_invalid(form)


class PositionUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'positions/position_form.html'
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


class PositionDeleteView(EditorModeratedDeleteView):
    model = Position
    template_name = 'positions/position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')
    confirm_url_name = 'employees:position_delete_confirm'
    permission_required = 'employees.delete_position'


class PositionDeleteConfirmView(EditorModeratedDeleteView):
    model = Position
    template_name = 'positions/position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')
    confirm_url_name = 'employees:position_delete_confirm'
    permission_required = 'employees.delete_position'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.username
        if request.user.groups.filter(name=settings.MTO_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление должности: %s пользователем из группы MTO: %s',
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
            'Отказано в подтверждении удаления должности: %s пользователем: %s',
            obj,
            user)
        return self.render_to_response(self.get_context_data())
