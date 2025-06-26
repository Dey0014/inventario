from inventario.imp import *

@login_required
def agregar_material(request):
    if request.method == "POST" :
        codigo = request.POST.get('codigo')
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad')
        tipo = request.POST.get('tipo')

        if not codigo:
            codigo=generar_codigo(tipo)
            print(codigo)
        
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
                details=f"Se agregaron {cantidad} del material {material.descripcion} con codigo ({material.codigo})",
            )
            return JsonResponse({'success': True, 'message': "Material registrado correctamente."})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})

    return JsonResponse({'success': False, 'message': "Solicitud no válida."})

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
            details=f"Se elimino {material.descripcion} con el codigo {material.codigo} por el motivo de {motivo}",
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
        cantidad_minima = request.POST.get('cantidad_minima')
        tipo = request.POST.get('tipo')

        if not codigo:
            codigo=generar_codigo(tipo)
            print(codigo)

        # Encuentra el material por su código o ID
        try:
            material = get_object_or_404(Material, pk=pk)
            material.codigo = codigo
            material.descripcion = descripcion
            material.cantidad_minima = cantidad_minima
            material.tipo_material = tipo
            material.coordinador = request.user
            material.save()

            # Registrar la acción en el log
            UserActionLog.objects.create(
            user=request.user,
            action='Modifico Material',
            details=f"Se modifico el material con el codigo {material.codigo} por el usuario {request.user}",
            )

            return JsonResponse({'status': 'success'}, status=200)
        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

@login_required
def entregar_material_prueba(request, pk):
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            analista_id = request.POST.get('analista')
            persona_id = request.POST.get('persona')
            nombre = request.POST.get("nombre")
            cedula = request.POST.get("cedula")
            departamento_id = request.POST.get('departamento')
            nuevo_departamento = request.POST.get('nuevo_dep')
            descripcion = request.POST.get('descripcion')
            cantidad = int(request.POST.get('cantidad'))
            material_id = request.POST.get('material')


            
            # Validar y crear/obtener el departamento
            if nuevo_departamento or departamento_id:
                if departamento_id == "":
                    departamento = Departamento.objects.create(nombre=nuevo_departamento)
                else:
                    departamento = get_object_or_404(Departamento, id=departamento_id)
                    # Crear o seleccionar la persona

            if persona_id == "":
                persona = Personas.objects.create(
                    nombre=nombre,
                    cedula=cedula,
                    departamento=departamento
                )
            else:
                persona = get_object_or_404(Personas, id=persona_id)
            
            
            material = Material.objects.get(id=material_id)
            
            
            # Obtener el analista
            analista = User.objects.get(id=analista_id)
            # Crear el préstamo
            entrega = Entrega(
                material=material,
                materialID=material,
                analista=analista,
                cantidad=cantidad,
                descripcion=descripcion,
                persona=persona,
                tipo=material.tipo_material
            )
            entrega.save()

            UserActionLog.objects.create(
                user=request.user,
                action='entrega',
                details=f'Entregó {cantidad} de {material.descripcion} codigo {material.codigo} a {persona.nombre} por motivo de {descripcion}'
            )
            # Descontar la cantidad y guardar el material
            material.cantidad -= cantidad
            material.save()



            return redirect("material_list")

        except Exception as e:
            # Manejo genérico de errores
            print(f"Error: {e}")
            return redirect("material_list")

    return render(request, "extends/entrega.html")

@login_required
@group_required("coordinadores")
def modificar_cantidades(request, pk):
    if request.method == 'POST':
        cantidad_a_agregar = request.POST.get('cantidad')
        cantidad_a_restar = request.POST.get('restar')
        justificacion = request.POST.get('justificacion')

        try:
            # Obtener el material por pk (ID)
            material = Material.objects.get(pk=pk)

            # Realiza las operaciones de agregar o restar cantidades
            if cantidad_a_agregar:
                cantidad_a_agregar = int(cantidad_a_agregar)
                material.agregar_material(cantidad_a_agregar)
                mensaje_agregar = f"Se agregaron {cantidad_a_agregar} unidades al material {material.descripcion} con el codigo {material.codigo}."
                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='agregar material',
                    details=f"Se agregó {cantidad_a_agregar} unidades a {material.descripcion} con el codigo {material.codigo} por motivo de {justificacion}.",
                )

            if cantidad_a_restar:
                cantidad_a_restar = int(cantidad_a_restar)
                material.restar_material(cantidad_a_restar)
                mensaje_restar = f"Se restaron {cantidad_a_restar} unidades al material {material.descripcion} con el codigo {material.codigo}."

                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='restar material',
                    details=f"Se restaron {cantidad_a_restar} unidades al material {material.descripcion} con el codigo {material.codigo} por motivo de {justificacion}.",
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
def entregas_lotes(request):
    materiales = Material.objects.all()
    personas = Personas.objects.all()
    return render(request, "extends/entregasenlote.html",{'materiales':materiales,'personas':personas})

@login_required
@csrf_exempt
def registrar_entregas_lote(request):
    if request.method == 'POST':
        try:
            # Obtener los datos enviados desde el formulario
            items_json = request.POST.get('items_json')
            persona_id = request.POST.get('persona')

            if not items_json or not persona_id:
                return JsonResponse({'error': 'Faltan datos obligatorios'}, status=400)

            items = json.loads(items_json)
            persona = Personas.objects.get(id=persona_id)

            for item in items:
                material = Material.objects.get(id=item['id'])

                # Validar si hay suficiente cantidad disponible
                if material.cantidad < int(item['cantidad']):
                    return JsonResponse({'error': f"No hay suficiente cantidad de {material.descripcion} codigo {material.codigo}."}, status=400)

                # Registrar el préstamo
                Entrega.objects.create(
                    material=material.descripcion,
                    persona=persona,
                    analista=request.user.username,
                    cantidad=item['cantidad'],
                    descripcion=item['descripcion'],
                    tipo=item['tipo'],
                    materialID=material
                )

    
                UserActionLog.objects.create(
                    user=request.user,
                    action='Entrega',
                    details=f'Entregó {item["cantidad"]} de {material.descripcion} codigo {material.codigo} a {persona.nombre} por motivo de {item["descripcion"]}'
                )
                # Actualizar la cantidad disponible del material
                material.restar_material(int(item['cantidad']))

            messages.success(request, "las entregas se han registrado correctamente.")
            return redirect("entregas_lotes")
        except Exception as e:
            # Manejo genérico de errores
            print(f"Error: {e}")
            messages.error(request, "Ocurrió un error al procesar la solicitud.")
            return redirect("entregas_lotes")
        
@login_required
def retorno(request, pk):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        justificacion = request.POST.get('justificacion')
        registroid = int(request.POST.get('registro'))

        # Encuentra el material por su código o ID
        try:
            registro = get_object_or_404(Entrega, pk=registroid)
            registro.cantidad -= cantidad
            registro.save()
            material = get_object_or_404(Material, pk=pk)
            material.cantidad += cantidad
            material.save()

            # Registrar la acción en el log
            UserActionLog.objects.create(
            user=request.user,
            action='Retorno',
            details=f" se regreso {cantidad} del material {material.descripcion} con el codigo {material.codigo} por motivo de {justificacion}.",
            )

            return JsonResponse({'status': 'success'}, status=200)
        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)




