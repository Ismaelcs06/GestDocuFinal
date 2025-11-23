"""
URL configuration for GestDocSi2 project.

This file defines the main URL routing for the project.
Each app manages its own URL configuration via include().
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from portal.views import home

#  Para servir archivos subidos por los usuarios (como PDF)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #  Portal público
    path("", home, name="home"),

    #  Autenticación y administración
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    #  Dashboard (inicio interno tras login)
    path("panel/", include("dashboard.urls")),

    #  Gestión de usuarios y actores
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    
    # Gestion del chatbot
    path("chat/", include("chat.urls", namespace="chat")),

    #  Gestión de casos y expedientes
    path("casos/", include(("casos.urls", "casos"), namespace="casos")),

    #  Gestión de documentos
    path("documentos/", include(("documentos.urls", "documentos"), namespace="documentos")),
    
    # Gestion de Bitacora
    
    path("seguridad/", include(("seguridad.urls", "seguridad"), namespace="seguridad")),
    
    # Gestión de reportes
    
    path("reportes/", include(("reportes.urls", "reportes"), namespace="reportes")),


]


# ⚙️ Configuración para servir archivos MEDIA en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
