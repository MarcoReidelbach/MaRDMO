from django.apps import AppConfig


class SensorConfig(AppConfig):
    name = 'MaRDMO'
    label = 'MaRDMO'
    verbose_name = 'MaRDMO Plugin'

    def ready(self):
        from . import handlers
