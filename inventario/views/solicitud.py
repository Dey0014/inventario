from inventario.imp import *


def crear_solicitud_con_items(persona, items):
    solicitud = Solicitudes.objects.create(persona=persona)
    for item in items:
        SolicitudItem.objects.create(
            solicitud=solicitud,
            articulo_id=item["id"],
            articulo_solicitado=item["nombre"],
            cantidad=item["cantidad"],
            tipo=item["tipo"],
            encargado=item["encargado"],
            uso=item["uso"]
        )

@cedula_required
def solicitud_material(request):
    ci = request.session.get('persona_cedula')
    persona = Personas.objects.filter(cedula=ci).first()

    if not persona:
        messages.error(request, "No se ha encontrado la persona.")
        return redirect("login_solicitud")

    if request.method == "POST":
        items_json = request.POST.get("items_json")

        if not items_json:
            messages.error(request, "No se enviaron artículos.")
            return redirect("Solicitud")

        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            messages.error(request, "Error al procesar los datos.")
            return redirect("Solicitud")

        if not items:
            messages.error(request, "No se han agregado artículos a la solicitud.")
            return redirect("Solicitud")

        crear_solicitud_con_items(persona, items)
        messages.success(request, "Solicitud registrada correctamente.")
        return redirect("Solicitud")

    cantidad_solicitudes = SolicitudItem.objects.filter(solicitud__persona__cedula=ci).count()

    context = {
        "solicitudePorPersona": cantidad_solicitudes,
        "materiales": Material.objects.filter(cantidad__gt=0, eliminado=False),
        "herramientas": Herramientas.objects.filter(cantidad__gt=0),
    }
    return render(request, 'solicitudes/solicitud_material.html', context)


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
            solicitud = get_object_or_404(SolicitudItem, id=id)
            if solicitud.tipo == 'Material':

                # Validar que la cantidad solicitada esté disponible
                material = get_object_or_404(Material, id=solicitud.articulo_id) 
                if solicitud.cantidad > material.cantidad or material.cantidad <= 0:
                    return JsonResponse({'success': False, 'message': 'Cantidad insuficiente en inventario.'}, status=400)

                # Registrar la entrega en el modelo Entrega
                entrega = Entrega.objects.create(
                    material=material,
                    tipo=material.tipo_material,
                    persona=solicitud.solicitud.persona,
                    analista=request.user.username,  # Asume que el usuario actual es el analista
                    cantidad=solicitud.cantidad,
                    descripcion=motivo,
                )
                material.cantidad -= solicitud.cantidad 
                material.save()

            else:
                # Validar que la cantidad solicitada esté disponible
                herramienta = get_object_or_404(Herramientas, id=solicitud.articulo_id) 
                if solicitud.cantidad > herramienta.cantidad or herramienta.cantidad <= 0:
                    return JsonResponse({'success': False, 'message': 'Cantidad insuficiente en inventario.'}, status=400)

                # Registrar la entrega en el modelo Entrega
                Prestamo = Prestamos.objects.create(
                    herramienta=herramienta,
                    persona=solicitud.solicitud.persona,
                    analista=request.user.username,  # Asume que el usuario actual es el analista
                    cantidad=solicitud.cantidad,
                    descripcion=motivo,
                    herramienta_id=herramienta.id
                )
                herramienta.cantidad -= solicitud.cantidad 
                herramienta.save()



            UserActionLog.objects.create(
            user=request.user,
            action='entrega',
            details=f'Entregó {solicitud.cantidad} de {solicitud.articulo_solicitado} por {motivo}')
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

@csrf_exempt
def descartar_solicitud(request, id):
    if request.method == 'DELETE':
        try:
            solicitud = SolicitudItem.objects.get(id=id)
            data = json.loads(request.body)
            motivo = data.get('motivo', '').strip()
            if not motivo:
                return JsonResponse({'success': False, 'message': 'La justificación es obligatoria.'}, status=400)

            UserActionLog.objects.create(
            user=request.user,
            action='Descarte',
            details=f'Se descarto la solicitud de {solicitud.cantidad} - {solicitud.articulo_solicitado} de {solicitud.solicitud.persona.nombre} por motivo {motivo}')
            # Actualizar el estado de la solicitud
            solicitud.delete()
            return JsonResponse({'success': True, 'message': 'Solicitud eliminada correctamente.'})
        except Solicitudes.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Solicitud no encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@cedula_required
def obtener_solicitudes_pendientes(request):
    ci = request.session.get('persona_cedula')

    solicitudes = SolicitudItem.objects.filter(
        solicitud__persona__cedula=ci
    ).values(
        'id',
        'articulo_solicitado',
        'articulo_id',
        'cantidad',
        'tipo',
        'solicitud__persona__nombre',
        'solicitud__persona__departamento__nombre'
    )

    data = list(solicitudes)
    return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)


def eliminar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudItem, id=pk)

    # # Validar que la solicitud pertenezca al usuario que la quiere eliminar
    # if solicitud.persona.usuario != request.user:
    #     messages.error(request, "No tienes permiso para eliminar esta solicitud.")
    #     return redirect('bandeja_solicitudes')

    # if solicitud.estado != 'pendiente':
    #     messages.warning(request, "Solo se pueden eliminar solicitudes pendientes.")
    #     return redirect('bandeja_solicitudes')

    solicitud.delete()
    messages.success(request, "Solicitud eliminada exitosamente.")
    return redirect("Solicitud")