from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from backend import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = routers.DefaultRouter()
#router.register(r'users', views.UserViewSet)
router.register(r'denuncias', views.DenunciaViewSet)
router.register(r'lista', views.ListaViewSet)

admin.site.site_header = 'Administrador de denuncias'

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'backend.views.home', name='home'),
    #url(r'^$', 'backend.views.buscar', name='home'),
    url(r'^buscar/(?P<numero>.+)/$', views.buscar, name='buscar'),
    url(r'^buscar/$', views.buscar, name='buscar'),
    url(r'^denuncia/$', views.denuncia, name='denuncia'),
    url(r'^descargar/$', views.download, name='descargar'),
    url(r'^descargar/(?P<formato>.+)/$', views.download, name='archivos'),

    # url(r'^blog/', include('blog.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()