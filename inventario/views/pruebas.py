from inventario.imp import *
from django.http import JsonResponse, HttpResponseNotAllowed

@login_required
def registroDePersonas(request):

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cedula = request.POST.get('cedula')
        departamentoid = request.POST.get('departamento')
        ubicacion = request.POST.get('ubicacion')

        departamento = Departamento.objects.get(id=departamentoid)

        persona = Personas.objects.create(
                nombre=nombre,
                cedula=cedula,
                departamento=departamento,
                ubicacion=ubicacion
            )
    departamentos = Departamento.objects.all() 
    return render(request, "extends/registrar_personas.html", { 'departamentos': departamentos })

@csrf_exempt
def crear_departamento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        if nombre:
            departamento = Departamento.objects.create(nombre=nombre)
            return JsonResponse({'id': departamento.id, 'nombre': departamento.nombre})
        else:
            return JsonResponse({'error': 'Nombre vacío'}, status=400)
    else:
        # Si entra un GET u otro método, devuelve error adecuado
        return HttpResponseNotAllowed(['POST'])
    
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
