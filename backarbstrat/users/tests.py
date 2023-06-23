from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
from django.urls import reverse
from users.models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework.test import APIClient
import os
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class LoginTestCase(TestCase):

    def setUp(self):
        # Creamos un cliente de prueba
        self.client = Client()

        # Creamos un usuario de prueba
        self.test_user = User.objects.create_user(username='testuser', email='test@test.com', password='testpassword')

    def test_login_success(self):
        # Datos de inicio de sesión válidos
        login_data = {
            'email': 'test@test.com',
            'password': 'testpassword',
        }

        # Codificar los datos en JSON
        json_data = json.dumps(login_data)

        # Realizar la petición POST a la vista de login
        response = self.client.post('/login/', data=json_data, content_type='application/json')

        # Comprobar que la respuesta tiene un código de estado 200 (éxito)
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        # Datos de inicio de sesión inválidos
        login_data = {
            'email': 'test@test.com',
            'password': 'wrongpassword',
        }

        # Codificar los datos en JSON
        json_data = json.dumps(login_data)

        # Realizar la petición POST a la vista de login
        response = self.client.post('/login/', data=json_data, content_type='application/json')

        # Comprobar que la respuesta tiene un código de estado 401 (no autorizado)
        self.assertEqual(response.status_code, 401)

class UserRegistrationTest(TestCase):
    # Esta función se ejecuta antes de cada prueba
    def setUp(self):
        # Crear un cliente para hacer solicitudes
        self.client = Client()
        # Obtener la URL para la vista de registro de usuarios
        self.register_url = reverse('register')  # asumiendo que esta es la ruta a userRegister

    # Prueba el caso en que los datos de registro son válidos
    def test_user_registration_valid_data(self):
        # Datos para un nuevo usuario
        user_data = {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test_email@example.com',
        }
        # Hacer una solicitud POST a la URL de registro
        response = self.client.post(self.register_url, data=json.dumps(user_data), content_type='application/json')
        # Asegurarse de que se recibe un estado HTTP 201 (creado)
        self.assertEqual(response.status_code, 201)

    # Prueba el caso en que un nombre de usuario ya está en uso
    def test_user_registration_duplicate_user(self):
        # Crear un usuario en la base de datos
        user = CustomUser.objects.create(
            username='test_user',
            password='test_password',
            email='test_email@example.com'
        )
        # Datos para otro usuario con el mismo nombre de usuario
        user_data = {
            'username': 'test_user',
            'password': 'test_password2',
            'email': 'test_email2@example.com',
        }
        # Hacer una solicitud POST a la URL de registro
        response = self.client.post(self.register_url, data=json.dumps(user_data), content_type='application/json')
        # Asegurarse de que se recibe un estado HTTP 400 (solicitud incorrecta) porque el nombre de usuario ya está en uso
        self.assertEqual(response.status_code, 400)


class EmailVerificationTest(TestCase):
    # Esta función se ejecuta antes de cada prueba
    def setUp(self):
        # Crear un cliente para hacer solicitudes
        self.client = Client()
        # Obtener la URL para la vista de verificación de correo electrónico
        self.verify_url = reverse('verify')  # asumiendo que esta es la ruta a verify

    # Prueba el caso en que se proporciona un token de verificación válido
    def test_email_verification_valid_token(self):
        # Crear un usuario inactivo en la base de datos con un token de verificación
        user = CustomUser.objects.create(
            username='test_user',
            password='test_password',
            email='test_email@example.com',
            verification_token='valid_token',
            is_active=False,
        )
        # Hacer una solicitud GET a la URL de verificación con el token de verificación
        response = self.client.get(self.verify_url, {'token': 'valid_token'})
        # Asegurarse de que se recibe un estado HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Recargar el usuario de la base de datos
        user.refresh_from_db()
        # Comprobar que el usuario está ahora activo
        self.assertTrue(user.is_active)

    # Prueba el caso en que se proporciona un token de verificación inválido
    def test_email_verification_invalid_token(self):
        # Hacer una solicitud GET a la URL de verificación con un token inválido
        response = self.client.get(self.verify_url, {'token': 'invalid_token'})
        # Asegurarse de que se recibe un estado HTTP 400 (solicitud incorrecta)
        self.assertEqual(response.status_code, 400)

class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(username='test_user', email='test@example.com', password='test_password')

        # Generar un token JWT para el usuario
        self.token = str(AccessToken.for_user(self.user))

        # Incluir el token de acceso en el encabezado de las solicitudes HTTP
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)


    def create_user(self, username, email, password):
        user = get_user_model().objects.create_user(username=username, email=email, password=password)
        return user

    def test_get_current_user(self):
        response = self.client.get(reverse('currentUser'))
        self.assertEqual(response.status_code, 200)
        data = response.json()  # Obtener los datos en forma de diccionario
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)

    def test_user_name_update(self):
        response = self.client.post(reverse('userUpdate'), {'username': 'new_username'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username')

    def test_user_email_update(self):
        response = self.client.post(reverse('emailUpdate'), {'email': 'new_email@example.com'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new_email@example.com')

    def test_user_pass_update(self):
        response = self.client.post(reverse('passUpdate'), {'currentPassword': 'test_password', 'newPassword': 'new_password'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_img_update(self):
        with open('media/testAssets/fondoLndscape_web.jpg', 'rb') as img_file:
            response = self.client.post(reverse('imageUpdate'), {'profile_picture': img_file})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.profile_picture)

    def test_delete_user_image(self):
        # Obtener la ruta absoluta de la carpeta 'media' en tu proyecto
        media_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../media/'))
        
        # Obtener la ruta absoluta de la imagen de prueba dentro de la carpeta 'media/testAssets'
        image_path = os.path.join(media_root, 'testAssets/fondoLndscape_web.jpg')
        
        # Abrir la imagen y crear el objeto SimpleUploadedFile
        image = SimpleUploadedFile(name='test_img.jpg', content=open(image_path, 'rb').read(), content_type='image/jpeg')
        
        # Asignar la imagen al perfil del usuario y guardar
        self.user.profile_picture = image
        self.user.save()

        # Realizar la solicitud para eliminar la imagen
        response = self.client.post(reverse('deleteUserImage'))
        
        # Verificar el código de estado y comprobar que el perfil del usuario ahora no tiene imagen
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.profile_picture)

    def test_recovery_password(self):
        response = self.client.post(reverse('recoveryPassword'), data=json.dumps({'email': self.user.email}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, 'test_password')