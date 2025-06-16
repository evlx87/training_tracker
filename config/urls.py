from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include, reverse_lazy

from employees.errors import custom_403
from employees.views import IndexView

handler403 = custom_403


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('employees/', include('employees.urls')),
    path('departments/', include('departments.urls')),
    path('positions/', include('positions.urls')),
    path('trainings/', include('trainings.urls')),
    path('reports/', include('reports.urls')),
    path('instructions/', include('instructions.urls')),
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

