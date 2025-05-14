import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import *
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse

def solicitudes_pendientes(request):
    # Consultar solicitudes pendientes con detalles necesarios
    solicitudes_pendientes = SolicitudItem.objects.all().values(
        'id',  # ID de la solicitud
        'articulo_solicitado',
        'articulo_id',  # Descripción combinada
        'cantidad',  # Cantidad solicitada
        'tipo',  # Tipo de solicitud
        'solicitud__persona__nombre',  # Nombre de la persona
        'solicitud__persona__departamento__nombre'  # Departamento de la persona
    )
    
    cantidad_solicitudes = solicitudes_pendientes.count()  # Contar el número de solicitudes

    # Serializar las solicitudes pendientes para pasarlas al JavaScript
    solicitudes_pendientes_json = json.dumps(
        list(solicitudes_pendientes), 
        cls=DjangoJSONEncoder
    )

    return {
        'cantidad_solicitudes': cantidad_solicitudes,  # Pasar la cantidad
        'solicitudes_pendientes': solicitudes_pendientes_json  # JSON serializado
    }

