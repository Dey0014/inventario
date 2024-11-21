from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from .models import UserActionLog
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt


def group_required(*group_names):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if bool(request.user.groups.filter(name__in=group_names)):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "No tienes permiso para acceder a esta página.")
                    return redirect("home") 
            return redirect("login")
        return _wrapped_view
    return decorator

def home(request):
    return render(request, "extends/home.html")

# login, inicio y hacer logout
@login_required
def inicio(request):
    return render(request, "extends/home.html")


def solicitud_material(request):
    if request.method == "POST":
        persona_id = request.POST.get("persona")
        nombre = request.POST.get("nombre")
        cedula = request.POST.get("cedula")
        departamento_id = request.POST.get("departamento")
        nuevo_departamento = request.POST.get("nuevo_dep")
        material_id = request.POST.get("material")
        cantidad = int(request.POST.get('cantidad'))

        # Verificar que todos los datos necesarios estén presentes
        if not material_id or not cantidad :
            messages.error(request, "Por favor, complete todos los campos obligatorios.")
            return redirect("Solicitud")

# Validar si no se ha seleccionado un departamento ni se ha ingresado uno nuevo
        if nuevo_departamento or departamento_id:
                # Crear o seleccionar el departamento
            if departamento_id == "nuevo":
                departamento = Departamento.objects.create(nombre=nuevo_departamento)
            else:
                departamento = get_object_or_404(Departamento, id=departamento_id)

        # Crear o seleccionar la persona
        if persona_id == "nueva":
            persona = Personas.objects.create(
                nombre=nombre,
                cedula=cedula,
                departamento=departamento
            )
        else:
            persona = get_object_or_404(Personas, id=persona_id)

        # Obtener el material solicitado
        material = get_object_or_404(Material, id=material_id)

        # Crear la solicitud
        Solicitudes.objects.create(
            persona=persona,
            material_solicitado=material,
            cantidad=cantidad
        )

        messages.success(request, "La solicitud se ha registrado correctamente.")
        return redirect("Solicitud")

    context = {
        "personas": Personas.objects.all(),
        "materiales": Material.objects.filter(cantidad__gt=0, eliminado=False),
        "departamentos": Departamento.objects.all()
    }
    return render(request, 'extends/solicitud_material.html', context)

def login_view(request):
    materiales = Material.objects.filter(cantidad__gt=0, eliminado=False)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # messages.info(request, f"Estas iniciando secion con {username}.")
                return redirect("inicio")
            else:
                messages.error(request, "credenciales invalidas.")
        else:
            messages.error(request, "credenciales invalidas.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form, 'materiales': materiales})

@login_required
@group_required("coordinadores")
def agregar_material(request):
    tipo = Material.objects.all()

    if request.method == "POST":
        codigo = request.POST.get('codigo')
        descripcion = request.POST.get('descripcion')
        cantidad_a_agregar = int(request.POST.get('cantidad'))

        # Verificar si el material con el mismo código ya existe
        if Material.objects.filter(codigo=codigo).exists():
            messages.error(request, "El código ya existe en el inventario.")
        else:
            # Crear el nuevo material
            material = Material(
                codigo=codigo,
                descripcion=descripcion,
                cantidad=cantidad_a_agregar,
                tipo_material=request.POST.get('tipo'),
                coordinador=request.user,
                fecha_ingreso=datetime.now()
            )

            # Guardar el nuevo material en la base de datos
            material.save()

            # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='agregar material',
                details=f'Añadió {material.descripcion} con código {material.codigo}',
            )

            messages.success(request, "El material se ha registrado correctamente.")
            return redirect("agregar_material")

    # Si no es una solicitud POST, renderizar un formulario simple (o vacío)
    return render(request, "extends/agregar_material.html", {"tipo": tipo})
    
@login_required
@group_required("coordinadores")
def agregar_cantidad_material(request):
    codigos = Material.objects.all()
    if request.method == "POST":
        codigo = request.POST.get('codigo')
        cantidad_a_agregar = request.POST.get('cantidad')
        cantidad_a_restar = request.POST.get('restar')

        # Obtener el material por código
        material = Material.objects.get(codigo=codigo)

        if cantidad_a_agregar:
            cantidad_a_agregar = int(cantidad_a_agregar)
            material.agregar_material(cantidad_a_agregar)
            messages.success(
                request,
                f"Se agregó {cantidad_a_agregar} unidades al material {material.descripcion}.",
            )
            # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='agregar material',
                details=f"Se agregó {cantidad_a_agregar} unidades a {material.descripcion}.",
            )

        if cantidad_a_restar:
            cantidad_a_restar = int(cantidad_a_restar)
            material.restar_material(cantidad_a_restar)
            messages.success(
                request,
                f"Se restó {cantidad_a_restar} unidades al material {material.descripcion}.",
            )
            # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='restar material',
                details=f"Se restó {cantidad_a_restar} unidades al material {material.descripcion}.",
            )
    
    return render(
        request,
        "extends/cantidad_material.html",
        {"codigos": codigos},
    )

@login_required
@group_required("coordinadores")
def modificar_cantidades(request, pk):
    if request.method == 'POST':
        cantidad_a_agregar = request.POST.get('cantidad')
        cantidad_a_restar = request.POST.get('restar')

        try:
            # Obtener el material por pk (ID)
            material = Material.objects.get(pk=pk)

            # Realiza las operaciones de agregar o restar cantidades
            if cantidad_a_agregar:
                cantidad_a_agregar = int(cantidad_a_agregar)
                material.agregar_material(cantidad_a_agregar)
                mensaje_agregar = f"Se agregaron {cantidad_a_agregar} unidades al material {material.descripcion}."

                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='agregar material',
                    details=f"Se agregó {cantidad_a_agregar} unidades a {material.descripcion}.",
                )

            if cantidad_a_restar:
                cantidad_a_restar = int(cantidad_a_restar)
                material.restar_material(cantidad_a_restar)
                mensaje_restar = f"Se restaron {cantidad_a_restar} unidades al material {material.descripcion}."

                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='restar material',
                    details=f"Se restaron {cantidad_a_restar} unidades al material {material.descripcion}.",
                )
            
            # Combinamos los mensajes de éxito para enviar en la respuesta JSON
            mensajes = []
            if cantidad_a_agregar:
                mensajes.append(mensaje_agregar)
            if cantidad_a_restar:
                mensajes.append(mensaje_restar)

            return JsonResponse({'status': 'success', 'messages': mensajes}, status=200)

        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado.'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

# vista para listado de materiales
@login_required
def material_list(request):
    materiales = Material.objects.filter(eliminado=False).order_by('descripcion')
    return render(request, "extends/material_list.html", {"materiales": materiales})

@login_required
def prestar_material(request):

    materiales = Material.objects.filter(cantidad__gt=0, eliminado=False)
    departamentos = Departamento.objects.all()
    personas = Personas.objects.all()

    if request.method == "POST":
        nuevo_departamento = request.POST.get('nuevo_departamento')
        departamento_id = request.POST.get('departamento')
        material_id = request.POST.get('material')
        analista_id = request.POST.get('analista')
        descripcion = request.POST.get('descripcion')
        cantidad = int(request.POST.get('cantidad'))
        nueva_persona = request.POST.get('nueva_persona')
        persona_id = request.POST.get('nombre')
       
        # Validar si no se ha seleccionado un departamento ni se ha ingresado uno nuevo
        if not nuevo_departamento and not departamento_id:
            messages.error(request, "Debe seleccionar un departamento existente o ingresar uno nuevo.")
            return render(request, "extends/prestamo.html", {"materiales": materiales, "departamentos": departamentos, "personas":personas})
        
        if nuevo_departamento:
            departamento, _ = Departamento.objects.get_or_create(nombre=nuevo_departamento)
        else:
            departamento = Departamento.objects.get(id=departamento_id)

                # Validar si no se ha seleccionado un departamento ni se ha ingresado uno nuevo
        if not nueva_persona and not persona_id:
            messages.error(request, "Debe seleccionar una persona existente o ingresar una nueva.")
            return render(request, "extends/prestamo.html", {"materiales": materiales, "departamentos": departamentos, "personas":personas})
        
        if nueva_persona:
            persona, _ = Personas.objects.get_or_create(nombre=nueva_persona)
        else:
            persona = Personas.objects.get(id=persona_id)
            
        material = Material.objects.get(id=material_id)

         # Validar si la cantidad solicitada es mayor que la cantidad disponible
        if cantidad > material.cantidad:
            messages.error(request, f"La cantidad solicitada excede la cantidad disponible. Solo hay {material.cantidad} disponible.")
            return render(request, "extends/prestamo.html", {"materiales": materiales, "departamentos": departamentos, "personas":personas})

        analista = User.objects.get(id=analista_id)

        # Crear el préstamo
        prestamo = Prestamo(
            departamento=departamento,
            material=material,
            analista=analista,
            cantidad=cantidad,
            descripcion=descripcion,
            persona=persona
        )
        prestamo.save()

        # Actualizar la cantidad de material
        material.cantidad -= cantidad
        material.save()
        UserActionLog.objects.create(
            user=request.user,
            action='entrega',
            details=f'Entregó {cantidad} de {material.descripcion}')
        
        messages.success(request, "El préstamo se ha registrado correctamente.")
        return redirect("prestar_material")  # Redirige a una página de lista o de éxito
    
    return render(request, "extends/prestamo.html", {"materiales": materiales, "departamentos":departamentos, "personas":personas})

@login_required
def prestamo_list(request):
    registros = Prestamo.objects.all()
    return render(request, "extends/registro_prestamo.html", {"registros": registros})

def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            tipo_usuario = form.cleaned_data["tipo_usuario"]

            # Crear usuario
            user = User.objects.create_user(
                username=username, password=password, email=email
            )

            # Asignar grupo
            if tipo_usuario == "Coordinador":
                grupo = Group.objects.get(name="coordinadores")
            else:
                grupo = Group.objects.get(name="analistas")
            user.groups.add(grupo)

            return redirect(
                "registrar_usuario"
            )  # Redirige al login después de registrar
    else:
        form = RegistroUsuarioForm()

    UserActionLog.objects.create(
    user=request.user,
    action='view',
    details='Registro a un usuario'
    )
    return render(request, "extends/registrar_usuario.html", {"form": form})

@login_required
def desactivar_usuario(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()

    UserActionLog.objects.create(
    user=request.user,
    action='view',
    details='desactivo un usuario'
    )
    return redirect("users_list")  # Redirige a la lista de usuarios o a donde prefieras

@login_required
def activar_usuario(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()

    UserActionLog.objects.create(
    user=request.user,
    action='view',
    details='Activo un usuario'
    )
    return redirect("users_list")

@login_required
def users_list(request):
    users = User.objects.all().order_by('username')
    return render(request, "extends/lista_usuarios.html", {"users": users})

@login_required
def user_action_log(request):
    logs = UserActionLog.objects.all().order_by('-timestamp')
    return render(request, 'extends/user_action_log.html', {'logs': logs})

def eliminar_material(request, pk):
    if request.method == 'POST':
        material = get_object_or_404(Material, pk=pk)
        motivo = request.POST.get('motivo')

        # Marcar como eliminado
        material.eliminado = True
        material.save()

        # Registrar la eliminación
        EliminarRegistro.objects.create(
            material_nombre=material.descripcion,
            motivo=motivo,
            usuario=request.user
        )

        return JsonResponse({'status': 'success', 'message': 'El material ha sido eliminado correctamente.'}, status=200)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)
        
def editar_material(request, pk):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')

        # Encuentra el material por su código o ID
        try:
            material = get_object_or_404(Material, pk=pk)
            material.codigo = codigo
            material.descripcion = descripcion
            material.tipo_material = tipo
            material.save()

            return JsonResponse({'status': 'success'}, status=200)
        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

