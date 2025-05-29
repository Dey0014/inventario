from inventario.imp import *

@login_required
def inicio(request):
    return render(request, "extends/home.html")

@login_required
def check_session(request):
    """Verifica si la sesión sigue activa"""
    return JsonResponse({"status": "active"})

def login_view(request):            # Login de usuario
    if request.user.is_authenticated:
        logout(request)
        return redirect("login")
    
    if request.method == "POST":
        username_or_email = request.POST.get("username").lower()
        password = request.POST.get("password")

        if not username_or_email or not password:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("login")

        # Buscar si es un email
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username  # Obtener el username real
        except User.DoesNotExist:
            username = username_or_email  # Si no es un correo, asumir que es un username

        # Intentar autenticar con el username y contraseña
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("inicio")
        else:
            messages.error(request, "Credenciales inválidas.")
    
    return render(request, "login.html")

def login_solicitud(request):           # Login de solicitud
    if request.method == "POST":
        cedula = request.POST.get("cedula")
        persona = Personas.objects.filter(cedula=cedula).first()

        if not cedula:
            messages.error(request, "Debes ingresar tu cédula.")
            return redirect("login_solicitud")

        try:
            persona = Personas.objects.get(cedula=cedula)
            request.session['persona_cedula'] = persona.cedula
            messages.success(request, f"Bienvenido {persona.nombre}!")
            return redirect("Solicitud")  # Redirigir al módulo de solicitudes
        except Personas.DoesNotExist:
            messages.error(request, "Cédula no encontrada en el sistema.")
            return redirect("login_solicitud")
    return render(request, "solicitudes/login_solicitud.html")
