import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from employees.views import log_view_action, EditorModeratedDeleteView
from .forms import TrainingProgramForm
from .models import TrainingProgram

logger = logging.getLogger('trainings')


class TrainingProgramListView(LoginRequiredMixin, ListView):
    model = TrainingProgram
    template_name = 'trainings/training_list.html'
    context_object_name = 'trainings'
    paginate_by = 20

    @log_view_action('Запрошен список', 'программ обучения')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TrainingProgramCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'trainings/training_form.html'
    success_url = reverse_lazy('trainings:training_list')
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


class TrainingProgramUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = TrainingProgram
    form_class = TrainingProgramForm
    template_name = 'trainings/training_form.html'
    success_url = reverse_lazy('trainings:training_list')
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


class TrainingProgramDeleteView(EditorModeratedDeleteView):
    model = TrainingProgram
    template_name = 'trainings/training_confirm_delete.html'
    success_url = reverse_lazy('trainings:training_list')
    confirm_url_name = 'trainings:training_delete_confirm'
    permission_required = 'employees.delete_trainingprogram'
    context_object_name = 'training'


class TrainingProgramDeleteConfirmView(EditorModeratedDeleteView):
    model = TrainingProgram
    template_name = 'trainings/training_confirm_delete.html'
    success_url = reverse_lazy('trainings:training_list')
    confirm_url_name = 'trainings:training_delete_confirm'
    permission_required = 'employees.delete_trainingprogram'
    context_object_name = 'training'

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.username
        if request.user.groups.filter(name=settings.MODERATOR_GROUP_NAME).exists():
            logger.info(
                'Подтверждено удаление программы обучения: %s пользователем из группы модераторов: %s',
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
            'Только пользователь из группы Moderators может подтвердить удаление.')
        logger.warning(
            'Отказано в подтверждении удаления программы обучения: %s пользователем: %s',
            obj,
            user)
        return self.render_to_response(self.get_context_data())
