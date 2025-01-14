from .forms import *
import json
# el resto de importaciones están en forms.py


# decorador para las funciones dependiendo del grupo 
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

#------------------------------------------------------------------------------------

# login, inicio y hacer logout
@login_required
def inicio(request):
    return render(request, "extends/home.html")

@login_required
def home(request):
    return render(request, "extends/home.html")

def login_view(request):
        # Cerrar sesión si el usuario está autenticado
    if request.user.is_authenticated:
        logout(request)
        return redirect("login")
    
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
    return render(request, "login.html", {"form": form,})


#--------------------------------------


# vistas de agregar materiales
@login_required
def agregar_material(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        codigo = request.POST.get('codigo')
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad')
        tipo = request.POST.get('tipo')

        # Validación
        if Material.objects.filter(codigo=codigo).exists():
            return JsonResponse({'success': False, 'message': "El código ya existe en el inventario."})

        try:
            # Crear material
            material = Material.objects.create(
                codigo=codigo,
                descripcion=descripcion,
                coordinador=request.user,
                cantidad=int(cantidad),
                tipo_material=tipo
            )

                    # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='Agrego Material',
                details=f"Se agrego {material.descripcion} por el usuario {request.user}",
            )
            return JsonResponse({'success': True, 'message': "Material registrado correctamente."})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})

    return JsonResponse({'success': False, 'message': "Solicitud no válida."})

#----------------------------------------



# vista de entrega de materiales

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

@login_required
@csrf_exempt
def aprobar_solicitud(request, id):
    if request.method == 'POST':
        try:
            # Obtener datos del cuerpo de la solicitud
            data = json.loads(request.body)
            motivo = data.get('motivo', '').strip()

            if not motivo:
                return JsonResponse({'success': False, 'message': 'La justificación es obligatoria.'}, status=400)

            # Obtener la solicitud
            solicitud = get_object_or_404(Solicitudes, id=id)

            # Validar que la cantidad solicitada esté disponible
            material = solicitud.material_solicitado
            if solicitud.cantidad > material.cantidad:
                return JsonResponse({'success': False, 'message': 'Cantidad insuficiente en inventario.'}, status=400)

            # Registrar la entrega en el modelo Entrega
            entrega = Entrega.objects.create(
                material=material,
                persona=solicitud.persona,
                analista=request.user.username,  # Asume que el usuario actual es el analista
                cantidad=solicitud.cantidad,
                descripcion=motivo,
            )
            material.cantidad -= solicitud.cantidad 
            material.save()

            UserActionLog.objects.create(
            user=request.user,
            action='entrega',
            details=f'Entregó {solicitud.cantidad} de {material.descripcion} por {motivo}')
            # Actualizar el estado de la solicitud
            solicitud.delete()


            return JsonResponse({'success': True, 'message': 'Solicitud aprobada y entrega registrada.'})

        except Solicitudes.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'La solicitud no existe.'}, status=404)
        except Material.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El material solicitado no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required
def entregar_material(request):

    materiales = Material.objects.filter(cantidad__gt=0, eliminado=False)
    departamentos = Departamento.objects.all()
    personas = Personas.objects.all()

    if request.method == "POST":
        nuevo_departamento = request.POST.get('nuevo_dep')
        departamento_id = request.POST.get('departamento')
        material_id = request.POST.get('material')
        analista_id = request.POST.get('analista')
        descripcion = request.POST.get('descripcion')
        cantidad = int(request.POST.get('cantidad'))
        persona_id = request.POST.get('persona')
        nombre = request.POST.get("nombre")
        cedula = request.POST.get("cedula")
        
        if nuevo_departamento or departamento_id:
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
            
        material = Material.objects.get(id=material_id)

        # Validar si la cantidad solicitada es mayor que la cantidad disponible
        if cantidad > material.cantidad:
            messages.error(request, f"La cantidad solicitada excede la cantidad disponible. Solo hay {material.cantidad} disponible.")
            return redirect("entregar_material")

        analista = User.objects.get(id=analista_id)

        # Crear el préstamo
        entrega = Entrega(
            material=material,
            analista=analista,
            cantidad=cantidad,
            descripcion=descripcion,
            persona=persona
        )
        entrega.save()

        # Descontar la cantidad y guardar el cambio
        material.cantidad -= cantidad  # Restar la cantidad solicitada
        material.save()  # Guardar el cambio en la base de datos

        UserActionLog.objects.create(
            user=request.user,
            action='entrega',
            details=f'Entregó {cantidad} de {material.descripcion}')
        
        messages.success(request, "El préstamo se ha registrado correctamente.")
        return redirect("entregar_material")  # Redirige a una página de lista o de éxito
    
    return render(request, "extends/entrega.html", {"materiales": materiales, "departamentos":departamentos, "personas":personas})

@login_required
def entrega_list(request):
    registros = Entrega.objects.all()
    return render(request, "extends/registro_entrega.html", {"registros": registros})

#-------------------------------------------



# vista para generar u usuarios
@login_required
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
            UserActionLog.objects.create(
            user=request.user,
            action='view',
            details='Registro a un usuario'
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


#-------------------------------------------------------------------------------------------


# lista de materiales edicion eliminar modificar y mas


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

@login_required
def material_list(request):
    herramientas = Herramientas.objects.all().order_by('descripcion')
    limpieza = Material.objects.filter(eliminado=False, tipo_material="LIM" ).order_by('descripcion')
    papeleria = Material.objects.filter(eliminado=False, tipo_material="ppl" ).order_by('descripcion')
    pinturas = Material.objects.filter(eliminado=False, tipo_material="pin" ).order_by('descripcion')
    resguardos = Material.objects.filter(eliminado=False, tipo_material="res" ).order_by('descripcion')
    electromecanica = Material.objects.filter(eliminado=False, tipo_material="ELM" ).order_by('descripcion')
    plomeria = Material.objects.filter(eliminado=False, tipo_material="PLO" ).order_by('descripcion')
    electricidad = Material.objects.filter(eliminado=False,  tipo_material__in=["ELE", "CABLE"]).order_by('descripcion')
    prueba = Material.objects.filter(eliminado=False,  tipo_material= "FER" ).order_by('descripcion')
    tipos = Material.TIPO_MATERIAL_CHOICES

    context = {
        "limpieza": limpieza,
        "herramientas":herramientas,
        "papeleria": papeleria,
        "pinturas": pinturas,
        "resguardos":resguardos,
        "electromecanica":electromecanica,
        "plomeria":plomeria,
        "electricidad":electricidad,
        "prueba":prueba,
        "tipos":tipos
    }

    return render(request, "extends/material_list.html", context)

@login_required
def eliminar_material(request, pk):
    if request.method == 'POST':
        material = get_object_or_404(Material, pk=pk)
        motivo = request.POST.get('motivo')

        # Registrar la eliminación
        EliminarRegistro.objects.create(
            material_nombre=material.descripcion,
            motivo=motivo,
            usuario=request.user
        )

        # Registrar la acción en el log
        UserActionLog.objects.create(
            user=request.user,
            action='Elimino Material',
            details=f"Se elimino {material.descripcion} con el id {material.id} por el usuario {request.user}",
        )
        # Marcar como eliminado
        material.delete()



        return JsonResponse({'status': 'success', 'message': 'El material ha sido eliminado correctamente.'}, status=200)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

@login_required
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

            # Registrar la acción en el log
            UserActionLog.objects.create(
            user=request.user,
            action='Modifico Material',
            details=f"Se modifico el material con el id {material.id} por el usuario {request.user}",
            )

            return JsonResponse({'status': 'success'}, status=200)
        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

#---------------------------------------------------------------------