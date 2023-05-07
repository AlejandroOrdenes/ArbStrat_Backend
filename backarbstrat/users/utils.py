from rest_framework_simplejwt.tokens import AccessToken

def generate_jwt_token(user):
    # Generar el token de acceso utilizando el usuario proporcionado
    token = AccessToken.for_user(user)

    # Retornar el token como una cadena de texto
    return str(token)
