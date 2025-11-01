from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView

from . import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth urls
    path('auth/', include('django.contrib.auth.urls')),
    # Custom registration page - ИСПРАВЛЕНО
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url='/auth/login/'  # URL для перенаправления после успешной регистрации
    ), name='registration'),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
]

# Error handlers
handler404 = 'blogicum.views.page_not_found'
handler500 = 'blogicum.views.internal_server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)