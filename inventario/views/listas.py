from inventario.imp import *

@login_required
def material_list(request):
    departamentos = Departamento.objects.all()
    personas = Personas.objects.all()
    materiales = Material.objects.filter(cantidad__gt=0, eliminado=False)
    herramientas = Herramientas.objects.all().order_by('descripcion')
    limpieza = Material.objects.filter(eliminado=False, tipo_material="LIM" ).order_by('descripcion')
    papeleria = Material.objects.filter(eliminado=False, tipo_material="PPL" ).order_by('descripcion')
    pinturas = Material.objects.filter(eliminado=False, tipo_material="PIN" ).order_by('descripcion')
    resguardos = Material.objects.filter(eliminado=False, tipo_material="RES" ).order_by('descripcion')
    electromecanica = Material.objects.filter(eliminado=False, tipo_material="ELM" ).order_by('descripcion')
    plomeria = Material.objects.filter(eliminado=False, tipo_material="PLO" ).order_by('descripcion')
    electricidad = Material.objects.filter(eliminado=False,  tipo_material__in=["ELE", "CABLE"]).order_by('descripcion')
    prueba = Material.objects.filter(eliminado=False,  tipo_material= "prueba" ).order_by('descripcion')
    tipos = Material.TIPO_MATERIAL_CHOICES

    context = {
        "limpieza": limpieza,
        "papeleria": papeleria,
        "pinturas": pinturas,
        "resguardos":resguardos,
        "electromecanica":electromecanica,
        "plomeria":plomeria,
        "electricidad":electricidad,
        "prueba":prueba,
        "tipos":tipos,
        "herramientas":herramientas,
        "materiales":materiales,
        "departamentos":departamentos,
        "personas":personas,
    }

    return render(request, "extends/material_list.html", context)

@login_required
@group_required("coordinadores")
def ListaHerramientas(request):
    herramientas = Herramientas.objects.all().order_by('descripcion')
    condiciones = Herramientas.CONDICION_CHOICES
    personas = Personas.objects.all()

    return render(request, "extends/lista_herramientas.html", {"herramientas":herramientas, "condiciones": condiciones, "personas":personas})

@login_required
def entrega_list(request):
    registros = Entrega.objects.all()
    return render(request, "extends/registro_entrega.html", {"registros": registros})

@login_required
def herramientas_prestadas(request):

    prestamos = Prestamos.objects.all()
    condiciones = Herramientas.objects.all()


    return render(request, "extends/registro_prestamo.html", {"prestamos": prestamos, "condiciones": condiciones})
