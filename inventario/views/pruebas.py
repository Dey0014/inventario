from inventario.imp import *
from django.http import JsonResponse, HttpResponseNotAllowed

@login_required
def registroDePersonas(request):

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cedula = request.POST.get('cedula')
        departamento = request.POST.get('departamento')
        ubicacion = request.POST.get('ubicacion')

        persona = Personas.objects.create(
                nombre=nombre,
                cedula=cedula,

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