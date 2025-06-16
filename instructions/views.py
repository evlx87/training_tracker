import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Instruction
from employees.views import log_view_action

logger = logging.getLogger('instructions')


class InstructionListView(LoginRequiredMixin, ListView):
    model = Instruction
    template_name = 'instructions/instruction_list.html'
    context_object_name = 'instructions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.GET.get('sort_by', 'title')
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by == 'title':
            if sort_order == 'desc':
                queryset = queryset.order_by('-title')
            else:
                queryset = queryset.order_by('title')
        elif sort_by == 'category':
            if sort_order == 'desc':
                queryset = queryset.order_by('-category')
            else:
                queryset = queryset.order_by('category')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by'] = self.request.GET.get('sort_by', 'title')
        context['sort_order'] = self.request.GET.get('sort_order', 'asc')
        return context

    @log_view_action('Запрошен список', 'инструкций')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class InstructionDetailView(LoginRequiredMixin, DetailView):
    model = Instruction
    template_name = 'instructions/instruction_detail.html'
    context_object_name = 'instruction'

    @log_view_action('Открыта', 'инструкция')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
