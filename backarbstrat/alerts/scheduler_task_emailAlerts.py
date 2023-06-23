
from apscheduler.schedulers.background import BackgroundScheduler
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def checkZScorePairs():
    try:
        from cointegration_arbitrage.models import Cointegrated_Pairs
        from users.models import CustomUser
        from alerts.models import UserAlerts

        queryset = Cointegrated_Pairs.objects.all()
        users = CustomUser.objects.all()

        longOpportunities = []
        shortOpportunities = []

        for pair in queryset:
            crypto1 = pair.Crypto1_ID
            crypto2 = pair.Crypto2_ID
            z_score = pair.z_score
            ultimo_z_score = z_score[-1]
            # Realizar el procesamiento de los datos...
            if ultimo_z_score >= 2:
                short = f"SHORT POR ZSCORE {round(ultimo_z_score, 2)}, en el par: {crypto1} - {crypto2}"
                shortOpportunities.append(short)

            elif ultimo_z_score <= -2:
                long = f"LONG POR ZSCORE {round(ultimo_z_score, 2)} en el par: {crypto1} - {crypto2}"
                longOpportunities.append(long)

        for user in users:
            emailUser = user.email
            userId = user.id

            try:
                userAlert = UserAlerts.objects.get(user_id=userId)
                emailAlert = userAlert.email_alerts
            except Exception as err:
                print("Error" + err)

            if emailAlert:
                print(f"SENDIG EMAIL TO {emailUser}")

                sendAlertsEmails(emailUser, longOpportunities, shortOpportunities )

        # sendAlertsEmails()

    except Exception as er:
        print(er)
        print("Error to get DB: ", er)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(checkZScorePairs, 'interval', hours=1)
    scheduler.start()


@csrf_exempt
def sendAlertsEmails(userEmail, longs, shorts):
    try:
        longs_text = "\n".join(longs)
        shorts_text = "\n".join(shorts)
        message_text = f"Longs:\n{longs_text}\n\nShorts:\n{shorts_text}"

        requests.post(
            "https://api.mailgun.net/v3/sandbox24feb8053278454bbd67be03b650b59e.mailgun.org/messages",
            auth=("api", settings.ANYMAIL["MAILGUN_API_KEY"]),
            data={"from": f"ArbStrat Crypto Analisys <mailgun@{settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']}>",
                  "to": [userEmail],
                  "subject": "ZScore opportunities!!",
                  "text": message_text})

        return JsonResponse({'message': 'Alert sended'}, status=200)

    except Exception as err:
        return print({'message': 'Error to send Email Alert', "error": err}, status=401)
