from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('auth_app.urls')),
    path('', include('system_app.urls')),
    path('', include('academic_app.urls')),
    path('', include('resource_app.urls')),
    path('', include('finance_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
