# context_processors.py
import json
from .models import Solicitudes

def solicitudes_pendientes(request):
    # Consultar solicitudes pendientes
    solicitudes_pendientes = Solicitudes.objects.filter(estado='P').values('material_solicitado__descripcion', 'persona__nombre')
    cantidad_solicitudes = solicitudes_pendientes.count()  # Contar el número de solicitudes

    # Serializar las solicitudes pendientes para pasarlas al JavaScript
    solicitudes_pendientes_json = json.dumps(list(solicitudes_pendientes))

    return {
        'cantidad_solicitudes': cantidad_solicitudes,  # Pasar la cantidad
        'solicitudes_pendientes': solicitudes_pendientes_json
    }