from django.apps import AppConfig


class HubConfig(AppConfig):
    name = 'hub'

    def ready(self):
        from . import handlers  # noqa
