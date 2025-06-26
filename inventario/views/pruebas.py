from inventario.imp import *
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML



# pdf julio
def pdf_herramientas(request):
    herramientas = Herramientas.objects.all()
    usuario = request.user
    logo_url = request.build_absolute_uri(static('img/logo.png'))
    hoy = datetime.today()
    fecha = hoy.strftime("%-d/%-m/%Y, %-I:%M:%S %p")


    template = render_to_string('pdfs/reporte_herramientas.html', {
    'herramientas': herramientas,
    'request': request,
    'logo': logo_url,
    'fecha': fecha,
    'usuario' :usuario
    })


    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="productos_filtrados_por_rango.pdf"'

    pdf_file = HTML(string=template).write_pdf()
    response.write(pdf_file)

    return response

def preview_reporte_herramientas(request):
    herramientas = Herramientas.objects.all()
    return render(request, 'pdfs/reporte_herramientas.html', {
        'herramientas': herramientas,
    })


@csrf_exempt  # Si usas CSRF en producción, usa un token, pero para pruebas esto va bien
def pdf_materiales(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            titulo = data.get('titulo', 'Sin Título')
            materiales = data.get('materiales', [])
            usuario = request.user
            hoy = datetime.today()
            fecha = hoy.strftime("%-d/%-m/%Y, %-I:%M:%S %p")  # O puedes usar `datetime.now()`
            logo_url = request.build_absolute_uri(static('img/logo.png'))

            template = render_to_string('pdfs/reporte_materiales.html', {
                'materiales': materiales,
                'usuario': usuario,
                'fecha': fecha,
                'logo': logo_url,
                'titulo':titulo
            })

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="reporte_materiales.pdf"'

            pdf_file = HTML(string=template, base_url=request.build_absolute_uri()).write_pdf()
            response.write(pdf_file)
            return response

        except Exception as e:
            return HttpResponse(f"Error generando PDF: {e}", status=500)
    else:
        return HttpResponse("Método no permitido", status=405)