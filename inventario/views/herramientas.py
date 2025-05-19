from inventario.imp import *            #importaciones están en imp.py

@login_required
def editar_herramienta(request, pk):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        condicion = request.POST.get('condicion')
        cantidadMinima = request.POST.get('cantidad_minima')


        # Encuentra el material por su código o ID
        try:
            herramienta = get_object_or_404(Herramientas, pk=pk)
            herramienta.descripcion = descripcion
            herramienta.condicion = condicion
            herramienta.cantidad_minima = cantidadMinima    
            herramienta.coordinador = request.user
            herramienta.save()

            # Registrar la acción en el log
            UserActionLog.objects.create(
            user=request.user,
            action='Modifico Herramienta',
            details=f"Se modifico la Herramienta con el id {herramienta.id} por el usuario {request.user}",
            )

            return JsonResponse({'status': 'success'}, status=200)
        except Material.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Material no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

@login_required
def eliminar_herramienta(request, pk):
    if request.method == 'POST':
        herramienta = get_object_or_404(Herramientas, pk=pk)
        motivo = request.POST.get('motivo')

        # Registrar la eliminación
        EliminarRegistro.objects.create(
            material_nombre=herramienta.descripcion,
            motivo=motivo,
            usuario=request.user
        )

        # Registrar la acción en el log
        UserActionLog.objects.create(
            user=request.user,
            action='Elimino Herramienta',
            details=f"Se elimino {herramienta.descripcion} con el id {herramienta.id} por el usuario {request.user}",
        )
        # Marcar como eliminado
        herramienta.delete()



        return JsonResponse({'status': 'success', 'message': 'El material ha sido eliminado correctamente.'}, status=200)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

@login_required
@group_required("coordinadores")
def modificarCantidadesHerramientas(request, pk):
    if request.method == 'POST':
        cantidad_a_agregar = request.POST.get('cantidad')
        cantidad_a_restar = request.POST.get('restar')
        justificacion = request.POST.get('justificacion')

        try:
            # Obtener el material por pk (ID)
            herramienta = Herramientas.objects.get(pk=pk)

            # Realiza las operaciones de agregar o restar cantidades
            if cantidad_a_agregar:
                cantidad_a_agregar = int(cantidad_a_agregar)
                herramienta.agregar_herramienta(cantidad_a_agregar)
                mensaje_agregar = f"Se agregaron {cantidad_a_agregar} unidades al material {herramienta.descripcion}."

                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='agregar herramienta',
                    details=f"Se agregó {cantidad_a_agregar} unidades a {herramienta.descripcion}por motivo de {justificacion}.",
                )

            if cantidad_a_restar:
                cantidad_a_restar = int(cantidad_a_restar)
                herramienta.restar_herramienta(cantidad_a_restar)
                mensaje_restar = f"Se restaron {cantidad_a_restar} unidades al material {herramienta.descripcion}."

                # Registrar la acción en el log
                UserActionLog.objects.create(
                    user=request.user,
                    action='restar herramienta',
                    details=f"Se restaron {cantidad_a_restar} unidades al material {herramienta.descripcion}por motivo de {justificacion}.",
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
def devolucion_herramientas(request, pk):
    if request.method == "POST":
        try:
            
            # Obtener los datos enviados por AJAX
            cantidad = int(request.POST.get('cantidad'))
            herramienta_id = request.POST.get('herramientaId')

            # Obtener el préstamo y la herramienta
            prestamo = Prestamos.objects.get(id=pk)
            herramienta = Herramientas.objects.get(id=herramienta_id)

            # Sumar la cantidad de la herramienta al inventario
            herramienta.cantidad += cantidad
            herramienta.save()

            UserActionLog.objects.create(
                user=request.user,
                action='Regreso',
                details=f"Finalizo el Prestamo de {herramienta.descripcion}- {cantidad} unds a ({prestamo.persona.nombre}) "
            )

            # Eliminar el préstamo activo
            prestamo.delete()

            return JsonResponse({"success": True})

        except ObjectDoesNotExist:
            # Manejar error si el préstamo o la herramienta no existen
            return JsonResponse({"success": False, "error": "Préstamo o herramienta no encontrados."})

        except ValueError:
            # Manejar error si la cantidad no es un valor válido
            return JsonResponse({"success": False, "error": "Cantidad no válida."})

        except Exception as e:
            # Manejar otros errores inesperados
            return JsonResponse({"success": False, "error": str(e)})

    # Si el método no es POST, se devuelve error
    return JsonResponse({"success": False, "error": "Método no permitido."})

@login_required
def Prestamo_herramientas(request, pk):
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            analista_id = request.POST.get('analista')
            persona_id = request.POST.get('persona')
            descripcion = request.POST.get('descripcion')
            cantidad = int(request.POST.get('cantidad'))
            
            # Validar y crear/obtener el departamento

            persona = get_object_or_404(Personas, id=persona_id)
            herramienta =   get_object_or_404(Herramientas, id=pk)
            

            
            # Validar cantidad disponible
            if cantidad > herramienta.cantidad:
                messages.error(request, f"La cantidad solicitada excede la disponible ({herramientas.cantidad}).")
                return redirect("Prestamo_herramientas")
            
            # Obtener el analista
            analista = User.objects.get(id=analista_id)
            # Crear el préstamo
            prestamo = Prestamos(
                herramienta=herramienta,
                analista=analista,
                cantidad=cantidad,
                descripcion=descripcion,
                persona=persona
            )
            prestamo.save()

            # Descontar la cantidad y guardar el material
            herramienta.cantidad -= cantidad
            herramienta.save()

            # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='entrega',
                details=f'Entregó {cantidad} de {herramienta.descripcion} a {persona.nombre} por motivo de {descripcion}'
            )

            return redirect("herramientas_prestadas")

        except Exception as e:
            # Manejo genérico de errores
            print(f"Error: {e}")
            
            return redirect("herramientas_prestadas")

    return render(request, "extends/lista_herramientas.html",)

@login_required
def agregar_herramientas(request):
    if request.method == "POST" :
        descripcion = request.POST.get('descripcion')
        cantidad = request.POST.get('cantidad')
        condicion = request.POST.get('condicion')


        try:
            # Crear material
            herramienta = Herramientas.objects.create(
                descripcion=descripcion,
                coordinador=request.user,
                cantidad=int(cantidad),
                condicion=condicion
            )

                    # Registrar la acción en el log
            UserActionLog.objects.create(
                user=request.user,
                action='Agrego Herramienta',
                details=f"Se agregaron {cantidad} de la Herramienta {herramienta.descripcion} con id ({herramienta.id})",
            )
            return JsonResponse({'success': True, 'message': "Material registrado correctamente."})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error: {str(e)}"})

    return JsonResponse({'success': False, 'message': "Solicitud no válida."})

@login_required
def prestamolotes(request):
    herramientas = Herramientas.objects.all()
    personas = Personas.objects.all()
    return render(request, "extends/prestamoenlotes.html",{'herramientas':herramientas,'personas':personas})

@login_required
@csrf_exempt
def registrar_prestamos_lote(request):
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
                herramienta = Herramientas.objects.get(id=item['id'])

                # Validar si hay suficiente cantidad disponible
                if herramienta.cantidad < int(item['cantidad']):
                    return JsonResponse({'error': f"No hay suficiente cantidad de {herramienta.descripcion}"}, status=400)

                # Registrar el préstamo
                Prestamos.objects.create(
                    herramienta=herramienta,
                    persona=persona,
                    analista=request.user.username,
                    cantidad=item['cantidad'],
                    descripcion=item['descripcion'],
                )

                UserActionLog.objects.create(
                    user=request.user,
                    action='Prestamo',
                    details=f'Entregó {item["cantidad"]} de {herramienta.descripcion} a {persona.nombre} por motivo de {item["descripcion"]}'
                )
                # Actualizar la cantidad disponible de la herramienta
                herramienta.restar_herramienta(int(item['cantidad']))

            return JsonResponse({'success': 'Préstamos registrados correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)