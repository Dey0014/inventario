from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Material(models.Model):
    TIPO_MATERIAL_CHOICES = [
        ('FER', 'Ferretería'),
        ('MAN', 'Mantenimiento'),
    ]
    
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    cantidad = models.PositiveIntegerField(default=0)
    tipo_material = models.CharField(max_length=3, choices=TIPO_MATERIAL_CHOICES, default='FER',)
    coordinador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    eliminado = models.BooleanField(default=False)

# auto_now_add=True
    def __str__(self):
        return f'{self.descripcion} ({self.codigo})'

    def agregar_material(self, cantidad_a_agregar):
        self.cantidad += cantidad_a_agregar
        self.save()
    
    def restar_material(self, cantidad_a_restar):
        self.cantidad -= cantidad_a_restar
        self.save()
        
    def prestar_material(self, cantidad_a_prestar):
        if self.cantidad < cantidad_a_prestar:
            raise ValidationError("No hay suficiente cantidad en inventario para este préstamo.")
        self.cantidad -= cantidad_a_prestar
        self.save()

class Departamento(models.Model):
    nombre = models.CharField(max_length=250)
    
    def __str__(self):
        return self.nombre

class Personas(models.Model):
    nombre = models.CharField(max_length=150)
    cedula = models.IntegerField()
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.CharField(max_length=150)
    
    def __str__(self):
        return f'{self.nombre} - {self.cedula}'

class Solicitudes(models.Model):

    OPCIONES_ESTADO = [
        ('P', 'Pendiente'),
        ('A', 'Aprobada'),
    ]
    persona = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True)
    material_solicitado = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    tipo = models.CharField(150)
    estado = models.CharField   (max_length=20,
                                choices=OPCIONES_ESTADO, 
                                default='P')
    def __str__(self):
        return f'Solicitud de {self.material_solicitado} por {self.persona}'
    


class Prestamo(models.Model):
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    persona = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    analista = models.CharField(max_length=150)
    cantidad = models.PositiveIntegerField()
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=1000)

    def save(self, *args, **kwargs):
        material = self.material
        if material.cantidad < self.cantidad:
            raise ValidationError("No hay suficiente cantidad en inventario para este préstamo.")
        material.prestar_material(self.cantidad)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Préstamo de {self.cantidad} {self.material} a {self.persona}'
    

    
class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        # Agrega más tipos de acciones si es necesario
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)  # Para detalles adicionales

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
class EliminarRegistro(models.Model):
    material_nombre = models.CharField(max_length=255)
    motivo = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_nombre} eliminado por {self.usuario.username} el {self.fecha_eliminacion}"
    

    