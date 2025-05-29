from inventario.imp import *

@login_required
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"].lower()
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            tipo_usuario = form.cleaned_data["tipo_usuario"]

            # Validar el dominio del correo
            if not email.endswith("@elsistema.org.ve"):
                messages.error(request, "El correo debe ser del dominio @elsistema.org.ve")
                return render(request, "extends/registrar_usuario.html", {"form": form})


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

            messages.success(request, "Usuario registrado con éxito.")
            return redirect("registrar_usuario")
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
    es_Coordinador = 'coordinadores' in [group.name for group in request.user.groups.all()]

    return render(request, "extends/lista_usuarios.html", {"users": users,  'es_Coordinador' : es_Coordinador,})

@login_required
def user_action_log(request):
    logs = UserActionLog.objects.all().order_by('-timestamp')
    return render(request, 'extends/user_action_log.html', {'logs': logs })

@login_required
def editar_usuarios(request, pk):
    if request.method == 'POST':

        user = get_object_or_404(User, id=pk)

        username = request.POST.get("username")
        email = request.POST.get("email")
        group_name = request.POST.get("group")
        password = request.POST.get("password")

        # Validar que el correo termine en @elsistema.org.ve
        if not email.endswith("@elsistema.org.ve"):
            return JsonResponse({"success": False, "message": "El correo debe pertenecer al dominio @elsistema.org.ve"}, status=400)

        user.username = username
        user.email = email
        
                # Solo cambiar la contraseña si el campo no está vacío
        if password:
            user.set_password(password)

        if group_name:
            group = get_object_or_404(Group, name=group_name)  # Obtiene 
            user.groups.clear()  # Elimina el grupo anterior
            user.groups.add(group)  # Asigna el nuevo grupo
        user.save()


        return JsonResponse({"success": True, "message": "Usuario actualizado correctamente."})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=400)
