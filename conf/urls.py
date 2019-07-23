from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from backend import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'lista', views.ListaViewSet)
router.register(r'denuncias', views.DenunciaViewSet)
router.register(r'numeros', views.ListaUnicaViewSet)

admin.site.site_header = 'Administrador de denuncias'

urlpatterns = [
    path(r'', views.home, name='home'),
    path(r'buscar/<str:numero>/', views.buscar, name='buscar'),
    path(r'buscar/', views.buscar, name='buscar'),
    path(r'navegar/', views.navegar, name='navegar'),
    path(r'denuncia/', views.denuncia, name='denuncia'),
    path(r'descargar/', views.download, name='descargar'),
    path(r'top/', views.topDenuncias, name='top'),
    re_path(r'^descargar/(?P<formato>.+)/$', views.download, name='archivos'),
    path(r'contacto/', TemplateView.as_view(template_name='contacto.html')),
    path(r'legal/', TemplateView.as_view(template_name='legal.html')),
    path(r'api/', TemplateView.as_view(template_name='api.html')),
    #path(r'adminactions/', include('adminactions.urls')),
    path(r'api/v1/', include(router.urls)),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'admin/', admin.site.urls),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
