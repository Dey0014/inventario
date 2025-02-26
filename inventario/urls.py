from django.urls import path
from inventario.views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # --------------Incio y menus----------#
    path("", login_view, name="login"),
    path("inicio/", inicio, name="inicio"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("agregar_material/", agregar_material, name="agregar_material"),
    path("material_list/", material_list, name="material_list"),
    path("entrega_list/", entrega_list, name="entrega_list"),
    path('modificar_cantidades/<int:pk>/', modificar_cantidades, name="modificar_cantidades"),
    path('modificarCantidadesHerramientas/<int:pk>/', modificarCantidadesHerramientas, name="modificarCantidadesHerramientas"),
    path("ListaHerramientas/", ListaHerramientas, name="ListaHerramientas"),
    path("registrar_usuario/", registrar_usuario, name="registrar_usuario"),
    path("home/",home,name="home"),
    path('users_list/', users_list, name='users_list'),
    path('desactivar_usuario/<int:user_id>/', desactivar_usuario, name='desactivar_usuario'),
    path('activar_usuario/<int:user_id>/', activar_usuario, name='activar_usuario'),
    path('user_action_log', user_action_log, name='user_action_log'),
    path('eliminar_material/<int:pk>/', eliminar_material, name='eliminar_material'),
    path('eliminar_herramienta/<int:pk>/', eliminar_herramienta, name='eliminar_herramienta'),
    path('editar_material/<int:pk>/', editar_material, name='editar_material'),
    path('editar_herramienta/<int:pk>/', editar_herramienta, name='editar_herramienta'),
    path('Solicitud/', solicitud_material, name='Solicitud'),
    path('aprobar_solicitud/<int:id>/', aprobar_solicitud, name='aprobar_solicitud'),
    path('descartar_solicitud/<int:id>/', descartar_solicitud, name='descartar_solicitud'),
    path("entregar_material_prueba/<int:pk>/", entregar_material_prueba, name="entregar_material_prueba"),
    path("herramientas_prestadas/", herramientas_prestadas, name="herramientas_prestadas"),
    path("devolucion_herramientas/<int:pk>/", devolucion_herramientas, name="devolucion_herramientas"),
    
]

