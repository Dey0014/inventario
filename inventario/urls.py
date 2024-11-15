from django.urls import path
from inventario.views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # --------------Incio y menus----------#
    path("", login_view, name="login"),
    path("inicio/", inicio, name="inicio"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("agregar-material/", agregar_material, name="agregar_material"),
    path("material-list/", material_list, name="material_list"),
    path("prestamo_list/", prestamo_list, name="prestamo_list"),
    # Agregar esta línea para redirigir a la lista de materiales
    path(
        "agregar_cantidad_material/",
        agregar_cantidad_material,
        name="agregar_cantidad_material",
    ),
    path('modificar_cantidades/<int:pk>/', modificar_cantidades, name="modificar_cantidades"),
    path("prestar/", prestar_material, name="prestar_material"),
    path("registrar_usuario/", registrar_usuario, name="registrar_usuario"),
    path("home/",home,name="home"),
    path('users_list/', users_list, name='users_list'),
    path('desactivar_usuario/<int:user_id>/', desactivar_usuario, name='desactivar_usuario'),
    path('activar_usuario/<int:user_id>/', activar_usuario, name='activar_usuario'),
    path('user_action_log', user_action_log, name='user_action_log'),
    path('eliminar_material/<int:pk>/', eliminar_material, name='eliminar_material'),
    path('editar_material/<int:pk>/', editar_material, name='editar_material'),
    path('Solicitud/', solicitud_material, name='Solicitud'),

]
