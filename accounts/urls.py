# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # === USUARIOS ===
    path("users/", views.users_list, name="user_list"),  
    path("users/create/", views.user_create, name="user_create"), 
    path("users/<int:user_id>/roles/", views.assign_roles, name="assign_roles"),
    path("users/<int:user_id>/actor/", views.actor_create, name="actor_create"),
    path("users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),


    # === ROLES ===
    path("roles/", views.roles_list, name="roles_list"),
    path("roles/create/", views.role_create, name="role_create"),
    path("roles/<int:pk>/edit/", views.role_update, name="role_update"),     # ✅ NUEVO
    path("roles/<int:pk>/delete/", views.role_delete, name="role_delete"),   # ✅ NUEVO

    # === ACTORES ===
    path("actors/", views.actors_list, name="actors_list"),
    path("actors/<int:actor_id>/abogado/", views.abogado_create, name="abogado_create"),
    path("actors/<int:actor_id>/cliente/", views.cliente_create, name="cliente_create"),
    path("actors/<int:actor_id>/asistente/", views.asistente_create, name="asistente_create"),
    path("actors/<int:pk>/", views.actor_detail, name="actor_detail"),

]
