from django.test import TestCase, Client
from django.urls import reverse
from inventario.models import Material
from django.contrib.auth.models import User

class AgregarMaterialTest(TestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_agregar_material(self):
        # Datos para el material
        data = {
            'codigo': 'MAT001',
            'descripcion': 'Tornillos',
            'cantidad': 50,
            'tipo': 'FER'
        }

        # Enviar una solicitud POST a la vista agregar_material
        response = self.client.post(reverse('agregar_material'), data)

        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)

        # Verificar que el material fue creado
        material = Material.objects.get(codigo='MAT001')
        self.assertEqual(material.descripcion, 'Tornillos')
        self.assertEqual(material.cantidad, 50)
        self.assertEqual(material.tipo_material, 'FER')
        
class agregarMaterialTest(TestCase):
    def setUp(self):
        # Crear un usuario para autenticación
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_agregar_material(self):
        # Datos para el material
        data = {
            'codigo': 'MAT001',
            'descripcion': 'Tornillos',
            'cantidad': 50,
            'tipo': 'FER'
        }

        # Enviar una solicitud POST a la vista agregar_material
        response = self.client.post(reverse('agregar_material'), data)

        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)

        # Verificar que el material fue creado
        material = Material.objects.get(codigo='MAT001')
        self.assertEqual(material.descripcion, 'Tornillos')
        self.assertEqual(material.cantidad, 50)
        self.assertEqual(material.tipo_material, 'FER')