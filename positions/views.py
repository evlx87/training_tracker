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

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация
        is_manager = self.request.GET.get('is_manager', '')
        is_teacher = self.request.GET.get('is_teacher', '')
        if is_manager == 'on':
            queryset = queryset.filter(is_manager=True)
        if is_teacher == 'on':
            queryset = queryset.filter(is_teacher=True)
        # Сортировка
        sort_by = self.request.GET.get('sort_by', 'name')  # По умолчанию сортировка по имени
        sort_order = self.request.GET.get('sort_order', 'asc')  # По умолчанию по возрастанию
        if sort_by == 'name':
            if sort_order == 'desc':
                queryset = queryset.order_by('-name')
            else:
                queryset = queryset.order_by('name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by'] = self.request.GET.get('sort_by', 'name')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')
        context['is_manager'] = self.request.GET.get('is_manager', '')
        context['is_teacher'] = self.request.GET.get('is_teacher', '')
        return context

    @log_view_action('Запрошен список', 'должностей')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PositionCreateView(
        LoginRequiredMixin,
        CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'positions/position_form.html'
    success_url = reverse_lazy('positions:position_list')
    permission_required = 'positions.add_position'

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
        UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'positions/position_form.html'
    success_url = reverse_lazy('positions:position_list')
    permission_required = 'positions.change_position'

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
    success_url = reverse_lazy('positions:position_list')
    confirm_url_name = 'positions:position_delete_confirm'
    permission_required = 'positions.delete_position'


class PositionDeleteConfirmView(EditorModeratedDeleteView):
    model = Position
    template_name = 'positions/position_confirm_delete.html'
    success_url = reverse_lazy('positions:position_list')
    confirm_url_name = 'positions:position_delete_confirm'
    permission_required = 'positions.delete_position'

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
