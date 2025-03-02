from django.apps import AppConfig


class ParfumuriConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parfumuri'

    def ready(self):
        import parfumuri.signals
