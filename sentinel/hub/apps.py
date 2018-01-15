from django.apps import AppConfig


class HubConfig(AppConfig):
    name = 'hub'

    def ready(self):
        from . import handlers  # noqa
        from guardian.models import Group
        from .utils import disconnect_all
        if not Group.objects.filter(name="default").exists():
            Group.objects.create(name="default")
        disconnect_all()