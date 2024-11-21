from django.contrib import admin

from .models import *

admin.site.register(Material)
admin.site.register(Departamento)
admin.site.register(Personas)
admin.site.register(Solicitudes)
admin.site.register(UserActionLog)
admin.site.register(EliminarRegistro)


