from django.apps import AppConfig


class CointegrationArbitrageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cointegration_arbitrage'

    scheduler_started = False

    def ready(self):
        global scheduler_started
        print("CointegrationArbitrageConfig ready() called")
        if not CointegrationArbitrageConfig.scheduler_started:
            CointegrationArbitrageConfig.scheduler_started = True
            # Se llama cuando se carga la aplicación Django
            from . import scheduler_task
            scheduler_task.start_scheduler()
            





    
