"""LegalBit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from Seguridad.views import custom_logout, custom_login, login_view
from Home.views import index as indexHome
from Seguridad.views import RegistroView as registrov, RegistrarseView, getProfile, change_password
from Investigaciones.views import index as investigacionIndex
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import (
handler400, handler403, handler404, handler500
)
admin.site.site_header = settings.ADMIN_SITE_HEADER
app_name = 'legalbit'
urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', LoginView.as_view(template_name='index.html'), name='index'),
    path('', indexHome, name='index'),
    path('Generales/', include('Generales.urls' , namespace='Generales')),
    path('Investigaciones/', include('Investigaciones.urls', namespace='Investigaciones')),
    path('Documentos/', include('Documentos.urls', namespace='Documentos')),
    path('Inmuebles/', include('Inmuebles.urls', namespace='Inmuebles')),
    #path('Investigaciones/', investigacionIndex , name='Investigaciones'),
    path('Normativas/', include('Normativas.urls', namespace='Normativas')),
    path('logout/', custom_logout, name='logout'),
    #path('registro/', registrov.as_view(), name="registro"),
    path('perfil',getProfile, name='ver perfil'),
    path('resetpsw', change_password, name='reset passsword'),
    path('registro', RegistrarseView, name='registro'),
    path('login/', login_view, name='login'),
    path('Personas/', include('Personas.urls', namespace='Personas')),
    path('Webhook/', include('Webhook.urls', namespace='Webhook')),
    path('Expedientes/', include('MisExpedientes.urls', namespace='Expedientes')),
    path('tickets/', include('TicketingSystem.urls', namespace='tickets')),
    path('Cobranzas/', include('MisCobranzas.urls', namespace='Cobranzas')),
    path('Credito/', include('CargarCredito.urls', namespace='Creditos')),
    path('Verificacion/', include('SignatureVerification.urls', namespace='Verificacion')),
]

# django.conf.urls.static.static() devuelve [] cuando DEBUG=False, asi que al apagar
# DEBUG dejaria de servirse /static/ y /media/. Se sirven explicitamente para no
# romper el sitio. Lo correcto es que nginx los sirva: ver bloques location del deploy.
from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
handler404 = 'Seguridad.views.handler404'
