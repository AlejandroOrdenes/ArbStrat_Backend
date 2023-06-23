import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from alerts.models import UserAlerts

# Create your views here.


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def updateEmailAlerts(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        emailAlert = data.get('emailAlert')

        try:
            user_alerts, created = UserAlerts.objects.get_or_create(user=user)
            user_alerts.email_alerts = emailAlert
            user_alerts.save()
            return JsonResponse({'message': 'Email alert settings updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateDiscordAlerts(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        discordAlert = data.get('discordAlert')

        try:
            user_alerts, created = UserAlerts.objects.get_or_create(user=user)
            user_alerts.discord_alerts = discordAlert
            user_alerts.save()
            return JsonResponse({'message': 'Discord alert settings updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserAlerts(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            user_alerts = UserAlerts.objects.get(user=user)
            return JsonResponse({
                'emailAlert': user_alerts.email_alerts,
                'discordAlert': user_alerts.discord_alerts,
            }, status=200)
        except UserAlerts.DoesNotExist:
            return JsonResponse({'message': 'No alert settings found for this user'}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        return JsonResponse({'message': 'User not authenticated'}, status=401)

    

    
