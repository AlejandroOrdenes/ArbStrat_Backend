import json
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from .models import CustomUser
from users.utils import generate_jwt_token
from django.views.decorators.csrf import csrf_exempt
import secrets
from urllib.parse import urlencode, urlunparse
import smtplib
from email.mime.text import MIMEText

@csrf_exempt
def login(request):
    if request.method == 'POST':
        # Decodificar el cuerpo de la petición como JSON
        data = json.loads(request.body) 

        email = data.get('email')
        password = data.get('password')

        # Autenticar al usuario
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generar el token JWT
            token = generate_jwt_token(user)

            # Retornar la respuesta con el token
            return JsonResponse({'token': token}, status=200)
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

@csrf_exempt
def userRegister(request):
    if request.method == 'POST':
        # Decodificar el cuerpo de la petición como JSON
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        print("Username:", username)
        print("Password:", password)
        print("Email:", email)

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'message': 'El usuario ya existe'}, status=400)

        # Genera un código de confirmación de 16 bytes en formato hexadecimal
        # verification_token = secrets.token_urlsafe(32)


        # Construye los componentes de la URL
        # scheme = 'http'
        # netloc = 'localhost:8000'
        # path = '/verify/'
        # params = None
        # query = urlencode({'token': verification_token})
        # fragment = None

        # Combina los componentes para formar la URL de verificación completa
        # verification_url = urlunparse((scheme, netloc, path, params, query, fragment))

        # print(verification_url)

        
        # send_verification_email(email, verification_url)
        
        # Crear un nuevo usuario
        user = CustomUser.objects.create_user(
            username=username, password=password, email=email)


        # Autenticar al usuario recién registrado
        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user is not None:
            # Generar y emitir el token JWT
            token = generate_jwt_token(authenticated_user)

            # Retornar la respuesta con el token
            return JsonResponse({'token': token}, status=201)

    return JsonResponse({'message': 'Método no permitido'}, status=405)


def send_verification_email(email, verification_url):
    # Configuración del servidor SMTP
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_username = "your_username"
    smtp_password = "your_password"

    # Crear el mensaje de correo electrónico
    subject = "Verificación de registro"
    body = f"Haz clic en el siguiente enlace para verificar tu registro: {verification_url}"
    sender = "alejandro.ordenes.o@gmail.com"
    receiver = email

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver

    # Enviar el correo electrónico
    try:
        smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
        smtp_obj.starttls()
        smtp_obj.login(smtp_username, smtp_password)
        smtp_obj.sendmail(sender, [receiver], message.as_string())
        smtp_obj.quit()
        print("Correo electrónico enviado correctamente")
    except Exception as e:
        print("Error al enviar el correo electrónico:", str(e))

def verifyUser(request):
    pass