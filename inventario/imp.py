from .models import *
from .forms import *
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime, date
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
from functools import wraps
import re
from django.templatetags.static import static




def generar_codigo(tipo_material):
    prefijo = PREFIJOS.get(tipo_material, tipo_material.upper())  # usa tipo_material si no está mapeado

    # Filtra los códigos existentes que empiezan con ese prefijo
    codigos = Material.objects.filter(
        tipo_material=tipo_material,
        codigo__startswith=prefijo
    ).values_list('codigo', flat=True)

    # Extrae los números y obtiene el máximo
    max_num = 0
    for codigo in codigos:
        match = re.search(rf'{prefijo}(\d+)', codigo)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    # Retorna el nuevo código
    nuevo_codigo = f"{prefijo}{max_num + 1}"
    return nuevo_codigo


# decorador para las funciones dependiendo del grupo 
def group_required(*group_names):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if bool(request.user.groups.filter(name__in=group_names)):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "No tienes permiso para acceder a esta página.")
                    return redirect("inicio") 
            return redirect("login")
        return _wrapped_view
    return decorator

def solicitud_view(request):
    if not request.session.get("solicitud_user_id"):  # Verificamos si está autenticado
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect("login_solicitud")

    return render(request, "solicitudes/solicitud.html")

def cedula_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('persona_cedula'):
            return redirect('login_solicitud')
        return view_func(request, *args, **kwargs)
    return _wrapped_view