import json
import random
import secrets
from urllib.parse import urlencode, urlunparse
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, JsonResponse
import requests
from django.conf import settings
from .models import CustomUser
from users.utils import generate_jwt_token
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.text import MIMEText
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


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
            print(token)
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
        verification_token = secrets.token_urlsafe(32)

        # Construye los componentes de la URL
        scheme = 'http'
        netloc = 'localhost:3000'
        path = '/verify/'
        params = None
        query = urlencode({'token': verification_token})
        fragment = None

        # Combina los componentes para formar la URL de verificación completa
        verification_url = urlunparse(
            (scheme, netloc, path, params, query, fragment))

        print(verification_url)

        # Crear un nuevo usuario (inactivo al principio)
        user = CustomUser.objects.create_user(
            username=username, password=password, email=email, is_active=False)

        # Guardar el token de verificación en el usuario
        user.verification_token = verification_token

        try:
            # Intentar enviar el correo de verificación
            sendVerificationEmail(email, verification_url)
        except Exception as e:
            # Si algo va mal, retorna un error
            return JsonResponse({'message': 'Error al enviar el correo de verificación: ' + str(e)}, status=500)

        # Si el correo se envía con éxito, guardar el usuario
        user.save()

        return JsonResponse({'message': 'Usuario creado con éxito, por favor verifica tu correo para activar la cuenta'}, status=201)


@csrf_exempt
def sendVerificationEmail(userEmail, url):
    try:

        message_text = f"Follow this link to register the account {url}"

        requests.post(
            "https://api.mailgun.net/v3/sandbox24feb8053278454bbd67be03b650b59e.mailgun.org/messages",
            auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
            data={"from": f"ArbStrat Crypto <mailgun@{settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']}>",
                  "to": [userEmail],
                  "subject": "Register account confirmation",
                  "text": message_text})

        return JsonResponse({'message': 'Alert sended'}, status=200)

    except Exception as err:
        return print({'message': 'Error to send Email Alert', "error": err}, status=401)


def verify(request):
    # Obtén el token de la URL
    token = request.GET.get('token')

    # Busca al usuario con este token
    try:
        user = CustomUser.objects.get(verification_token=token)
    except CustomUser.DoesNotExist:
        return JsonResponse({'message': 'Token inválido'}, status=400)

    # Activa al usuario y borra el token de verificación
    user.is_active = True
    user.verification_token = None
    user.save()

    # Redirecciona al usuario al login o muestra un mensaje de éxito
    return JsonResponse({'message': 'Cuenta activada con éxito'}, status=200)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUser(request):
    user = request.user
    data = {
        'password': user.password,
        'username': user.username,
        'email': user.email,
        'image_profile': user.image_url() if user.profile_picture else None,
        'is_superuser': user.is_superuser

    }
    return JsonResponse(data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userName_update(request):

    if request.method == 'POST':
        user = request.user

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=user.username).exists():
            username = request.data.get('username')

            if username:
                user.username = username
                user.save()
                return JsonResponse({'message': 'Update Username successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Error to process the username change'}, status=400)

        else:
            return JsonResponse({'message': 'User doesn´t exist'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userEmail_update(request):

    if request.method == 'POST':
        user = request.user

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=user.username).exists():
            email = request.data.get('email')

            if email:
                user.email = email
                user.save()
                return JsonResponse({'message': 'Update Email successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Error to process the email change'}, status=400)

        else:
            return JsonResponse({'message': 'User doesn´t exist'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userPass_update(request):

    if request.method == 'POST':
        user = request.user

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=user.username).exists():
            # Obtener la contraseña ingresada por el usuario
            currentPassword = request.data.get("currentPassword")
            newPassword = request.data.get('newPassword')

            # Comparar las contraseñas
            if user.check_password(currentPassword):
                # Las contraseñas coinciden
                try:
                    user.set_password(newPassword)
                    user.save()
                except Exception as e:
                    print("Error to process the pass update", str(e))

                return JsonResponse({'message': 'Update Password successfully'}, status=200)
            else:
                # Las contraseñas no coinciden
                return JsonResponse({'message': 'Error to process the pass update'}, status=400)

        else:
            return JsonResponse({'message': 'User doesn´t exist'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userImg_update(request):

    if request.method == 'POST':
        user = request.user

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=user.username).exists():
            image_file = request.FILES.get('profile_picture')

            if image_file:
                user.profile_picture = image_file
                user.save()
                return JsonResponse({'message': 'Update Profile Image successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Error to process the image'}, status=400)

        else:
            return JsonResponse({'message': 'User doesn´t exist'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteUserImage(request):

    if request.method == 'POST':
        user = request.user

        # Verificar si el usuario ya existe
        if CustomUser.objects.filter(username=user.username).exists():
            user.profile_picture.delete()  # Eliminar la imagen del perfil
            user.profile_picture = None  # Establecer el campo en None
            user.save()
            return JsonResponse({'message': 'Profile Image removed successfully'}, status=200)
        else:
            return JsonResponse({'message': 'User doesn´t exist'}, status=400)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redirect_to_admin(request):

    user = request.user

    # Verificar si el usuario es superusuario
    if user.is_superuser:
        return HttpResponseRedirect('/admin/')

    else:
        return JsonResponse({'message': 'User is not a superuser'}, status=403)

@csrf_exempt
def recoveryPassword(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        print(email)
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            
            # Generar contraseña provisional aleatoria
            provisional_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

            # Encriptar contraseña provisional
            hashed_password = make_password(provisional_password)

            # Actualizar contraseña del usuario
            user.password = hashed_password
            user.save()

            # Enviar correo electrónico de recuperación con contraseña provisional
            sendRecoveryEmail(email, provisional_password)

            return JsonResponse({'message': 'Recovery email sent'}, status=200)
        else:
            return JsonResponse({'message': 'User does not exist'}, status=400)
    else:
        return JsonResponse({'message': 'Error to process the password recovery'}, status=400)


def sendRecoveryEmail(email, password):
        try:

            message_text = f"Your temporary password is: {password}"

            requests.post(
                "https://api.mailgun.net/v3/sandbox24feb8053278454bbd67be03b650b59e.mailgun.org/messages",
                auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
                data={"from": f"ArbStrat Crypto <mailgun@{settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']}>",
                    "to": [email],
                    "subject": "Recovery account confirmation",
                    "text": message_text})

            return JsonResponse({'message': 'Alert sended'}, status=200)

        except Exception as err:
            return print({'message': 'Error to send Email Recovery', "error": err}, status=401)