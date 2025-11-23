from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import CasoViewSet, EquipoCasoViewSet, ParteProcesalViewSet, ExpedienteViewSet, CarpetaViewSet

# Crear el router y registrar los viewsets
""" router = DefaultRouter()
router.register(r'casos', CasoViewSet)
router.register(r'equipos_caso', EquipoCasoViewSet)
router.register(r'partes_procesales', ParteProcesalViewSet)
router.register(r'expedientes', ExpedienteViewSet)
router.register(r'carpetas', CarpetaViewSet)
 """
from . import views

app_name = "casos"

urlpatterns = [
   #  path('', include(router.urls)), 
    path("", views.caso_list, name="case_list"),
    path("crear/", views.caso_create, name="case_create"),
    path("<int:pk>/editar/", views.caso_edit, name="case_edit"),
    
    
    # EquipoCaso
    path("<int:caso_id>/equipo/", views.equipo_caso_list, name="equipo_list"),
    path("<int:caso_id>/equipo/agregar/", views.equipo_caso_add, name="equipo_add"),
    path("equipo/<int:pk>/eliminar/", views.equipo_caso_delete, name="equipo_delete"), 

    # Parte Procesal
    path("<int:caso_id>/partes/", views.parte_procesal_list, name="parte_list"),
    path("<int:caso_id>/partes/agregar/", views.parte_procesal_add, name="parte_add"),
    
    
    # Expedientes
    path("expedientes/", views.expediente_list, name="expediente_list"),
    path("<int:caso_id>/expediente/crear/", views.expediente_create, name="expediente_create"),
    
    # Carpetas
    path("expedientes/<int:expediente_id>/carpetas/", views.carpeta_list, name="carpeta_list"),
    path("expedientes/<int:expediente_id>/carpetas/crear/", views.carpeta_create, name="carpeta_create"),
    
    path("carpetas/", views.carpeta_global_list, name="carpeta_global_list"),

    #TimeLine

    path('expediente/<int:expediente_id>/timeline/', views.expediente_timeline, name='expediente_timeline'),

    path("expediente/<int:expediente_id>/", views.expediente_detail, name="expediente_detail"),
    path("caso/<int:caso_id>/expediente/", views.expediente_by_caso, name="expediente_by_caso"),
    
    path("carpeta/<int:carpeta_id>/", views.carpeta_detalle, name="carpeta_detalle"),


]
