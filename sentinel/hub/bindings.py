from .models import Hub, Leaf, Datastore, Condition
from .serializers import DatastoreSerializer, ConditionSerializer, LeafSerializer

from django.db.models.query import EmptyQuerySet
from django.db.models.signals import post_save, post_delete
from channels.generic.websocket import JsonWebsocketConsumer

class ModelBinding(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.subscribe_create = False
        self.subscribe_delete = False
        self.subscribe_update = False
        self._connect_to_model()
        super().__init__(*args, **kwargs)

    def _connect_to_model(self):
        post_save.connect(
            self.post_save_receiver,
            sender=self.model,
            dispatch_uid=id(self)
        )
        post_delete.connect(self.post_delete_receiver, sender=self.model, dispatch_uid=id(self))

    def _disconnect_from_model(self):
        post_save.disconnect(None, dispatch_uid=id(self))
        post_delete.disconnect(None, dispatch_uid=id(self))

    def disconnect(self, message):
        self._disconnect_from_model()
        super().disconnect(message)

    def post_save_receiver(self, instance, created, **kwargs):
        serializer = self.serializer_class(instance)
        if created and self.subscribe_create:
            self.send_json({
                'action': 'create',
                'data': serializer.data
            })
        elif self.subscribe_update:
            self.send_json({
                'action': 'update',
                'data': serializer.data
            })

    def post_delete_receiver(self, instance, **kwargs):
        if self.subscribe_delete:
            serializer = self.serializer_class(instance)
            self.send_json({
                'action': 'delete',
                'data': serializer.data
            })

    def get_instance(self, pk):
        return self.get_queryset().get(pk=pk)

    def get_queryset(self):
        return EmptyQuerySet()

    def receive_json(self, content):
        if 'action' not in content:
            return

        hub_id = self.scope["session"]["hub"]
        if content['action'] == 'subscribe':
            self.handle_subscribe(content.get('data', {}))
        elif content['action'] == 'retrieve':
            self.handle_retrieve(content.get('data', {}))
        elif content['action'] == 'list':
            self.handle_list()

    def handle_update(self, *args, **kwargs):
        print(list(args), dict(kwargs), "HERE")

    def handle_subscribe(self, message):
        if 'action' not in message:
            return

        if message['action'] in ['create', 'all']:
            self.subscribe_create = True
        if message['action'] in ['update', 'all']:
            self.subscribe_update = True
        if message['action'] in ['delete', 'all']:
            self.subscribe_delete = True

    def handle_retrieve(self, message):
        if 'pk' in message:
            instance = self.get_instance(message['pk'])
            serializer = self.serializer_class(instance)
            self.send_json({
                'action': 'retrieve',
                'data': serializer.data
            })

    def handle_list(self):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        self.send_json({
            'action': 'list',
            'data': serializer.data
        })


class HubBinding(ModelBinding):
    def connect(self):
        hub_id = int(self.scope["url_route"]["kwargs"]["id"])

        if Hub.objects.filter(id=hub_id).exists():
            self.scope["session"]["hub"] = hub_id
            self.accept()
        else:
            self.close()


class LeafBinding(HubBinding):
    model = Leaf
    serializer_class = LeafSerializer

    def get_queryset(self):
        hub_id = self.scope["session"]["hub"]
        return Hub.objects.get(id=hub_id).leaves.all()


class DatastoreBinding(HubBinding):
    model = Datastore
    serializer_class = DatastoreSerializer

    def get_queryset(self):
        hub_id = self.scope["session"]["hub"]
        return Hub.objects.get(id=hub_id).datastores.all()


class ConditionBinding(HubBinding):
    model = Condition
    serializer_class = ConditionSerializer

    def get_queryset(self):
        hub_id = self.scope["session"]["hub"]
        return Hub.objects.get(id=hub_id).conditions.all()
