from django.urls import path
from inventario.views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [

    # --------------Incio y menus----------#
    
    path("", login_view, name="login"),
    path("inicio/", inicio, name="inicio"),
    path("login_solicitud/", login_solicitud, name="login_solicitud"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # --------------Materiales----------#

    path("agregar_material/", agregar_material, name="agregar_material"),
    path("material_list/", material_list, name="material_list"),
    path("entrega_list/", entrega_list, name="entrega_list"),
    path('modificar_cantidades/<int:pk>/', modificar_cantidades, name="modificar_cantidades"),
    path('eliminar_material/<int:pk>/', eliminar_material, name='eliminar_material'),
    path('editar_material/<int:pk>/', editar_material, name='editar_material'),
    path("entregar_material_prueba/<int:pk>/", entregar_material_prueba, name="entregar_material_prueba"),
    path("entregas_lotes/", entregas_lotes, name="entregas_lotes"),
    path("registrar_entregas_lote/", registrar_entregas_lote, name="registrar_entregas_lote"),


    #---------------Personas----------#

    path("registroDePersonas/", registroDePersonas, name="registroDePersonas"),
    path('crear_departamento/', crear_departamento, name='crear_departamento'),

    # --------------Usuarios----------#

    path("registrar_usuario/", registrar_usuario, name="registrar_usuario"),
    path('users_list/', users_list, name='users_list'),
    path('desactivar_usuario/<int:user_id>/', desactivar_usuario, name='desactivar_usuario'),
    path('activar_usuario/<int:user_id>/', activar_usuario, name='activar_usuario'),
    path('editar_usuarios/<int:pk>/', editar_usuarios, name='editar_usuarios'),
    path("check_session/", check_session, name="check_session"),
    path('user_action_log', user_action_log, name='user_action_log'),

    # --------------Herramientas----------#

    path('modificarCantidadesHerramientas/<int:pk>/', modificarCantidadesHerramientas, name="modificarCantidadesHerramientas"),
    path("ListaHerramientas/", ListaHerramientas, name="ListaHerramientas"),
    path('eliminar_herramienta/<int:pk>/', eliminar_herramienta, name='eliminar_herramienta'),
    path('editar_herramienta/<int:pk>/', editar_herramienta, name='editar_herramienta'),
    path("herramientas_prestadas/", herramientas_prestadas, name="herramientas_prestadas"),
    path("devolucion_herramientas/<int:pk>/", devolucion_herramientas, name="devolucion_herramientas"),
    path('Prestamo_herramientas/<int:pk>/', Prestamo_herramientas, name='Prestamo_herramientas'),
    path('agregar_herramientas/', agregar_herramientas, name='agregar_herramientas'),
    path('prestamolotes/', prestamolotes, name='prestamolotes'),
    path('registrar-prestamos-lote/', registrar_prestamos_lote, name='registrar_prestamos_lote'),

    # --------------Solicitudes----------#

    path('Solicitud/', solicitud_material, name='Solicitud'),
    path('aprobar_solicitud/<int:id>/', aprobar_solicitud, name='aprobar_solicitud'),
    path('descartar_solicitud/<int:id>/', descartar_solicitud, name='descartar_solicitud'),
    path('obtener_solicitudes_pendientes/', obtener_solicitudes_pendientes, name='obtener_solicitudes_pendientes'),
    path('eliminar_solicitud/<int:pk>/', eliminar_solicitud, name='eliminar_solicitud'),
    
]

