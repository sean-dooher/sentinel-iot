from channels_api.bindings import ResourceBinding
from channels_api.permissions import BasePermission
from .models import Hub, Leaf, Datastore, Condition
from .serializers import DatastoreSerializer, ConditionSerializer, LeafSerializer


class LeafBinding(ResourceBinding):
    model = Leaf
    stream = "leaves"
    serializer_class = LeafSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return Hub.objects.get(id=self.kwargs['id']).leaves.all()


class DatastoreBinding(ResourceBinding):
    model = Datastore
    stream = "datastores"
    serializer_class = DatastoreSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return Hub.objects.get(id=self.kwargs['id']).datastores.all()


class ConditionBinding(ResourceBinding):
    model = Condition
    stream = "conditions"
    serializer_class = ConditionSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return Hub.objects.get(id=self.kwargs['id']).conditions.all()
