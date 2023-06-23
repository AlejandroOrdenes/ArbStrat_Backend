from django.apps import AppConfig

from alerts import scheduler_task_emailAlerts


class AlertsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alerts'

    scheduler_started = False

    def ready(self):
        print("AlertsConfig ready() called")
        if not self.scheduler_started:
            self.scheduler_started = True
            # Se llama cuando se carga la aplicación Django
            scheduler_task_emailAlerts.start_scheduler()