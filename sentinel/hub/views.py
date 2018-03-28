from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import DjangoObjectPermissions
from hub.models import Leaf, Device, Datastore, Condition, Hub
from hub.serializers import LeafSerializer, ConditionSerializer, DatastoreSerializer, HubSerializer
from .utils import validate_uuid, create_value, SentinelError
from .consumers import create_condition
from rest_framework import generics
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from guardian.models import Group as PermGroup
import secrets, json


class ObjectOnlyPermissions(DjangoObjectPermissions):
    def has_permission(self, request, view):
        return True


def demo_denied(request):
    raise PermissionDenied


def demo_conditions(request, id):
    if request.method == "GET":
        return render(request, "conditions.json")
    else:
        raise PermissionDenied


def demo_leaves(request, id):
    if request.method == "GET":
        return render(request, "leaves.json")
    else:
        raise PermissionDenied


def demo_hub(request):
    if request.method == "GET":
        return render(request, "hub.json")
    else:
        raise PermissionDenied


def demo_datastores(request, id):
    if request.method == "GET":
        return render(request, "datastores.json")
    else:
        raise PermissionDenied


def register_leaf(request, id):
    if request.method == 'POST':
        hub = get_object_or_404(Hub, id=id)
        if request.user.has_perm('delete_hub', hub):
            try:
                assert request.content_type in ['multipart/form-data', 'application/json', 'application/x-www-form-urlencoded']
                if request.content_type == 'application/json':
                    uuid = json.loads(request.body).get('uuid', None)
                else:
                    uuid = request.POST.get('uuid', None)
                assert uuid is not None
            except (KeyError, json.decoder.JSONDecodeError, AssertionError):
                return JsonResponse({'accepted': False, 'reason': 'Need uuid in message'})

            if not validate_uuid(uuid):
                return JsonResponse({'accepted': False, 'reason': 'Invalid uuid'})

            if User.objects.filter(username=f"{hub.id}-{uuid}").exists():
                User.objects.get(username=f"{hub.id}-{uuid}").delete()

            token = secrets.token_hex(16)
            user = User.objects.create_user(username=f"{hub.id}-{uuid}", password=token)
            return JsonResponse({'accepted': True, 'token': token})
        else:
            raise PermissionDenied
    else:
        return JsonResponse({"accepted": False, "reason": "Only available via POST"})


class HubList(generics.ListAPIView):
    serializer_class = HubSerializer
    permission_classes = [ObjectOnlyPermissions]

    def get_queryset(self):
        user = self.request.user
        return get_objects_for_user(user, 'view_hub', Hub.objects.all())

    def post(self, request, format=None):
        try:
            name = request.data['name']
        except KeyError:
            return JsonResponse({'accepted': False, 'reason': 'Missing name'})

        hub = Hub.objects.create(name=name)
        hub.save()

        hub_group = PermGroup.objects.get(name="hub-" + str(hub.id))
        request.user.groups.add(hub_group)

        return JsonResponse({'accepted': True})


class HubDetail(generics.RetrieveDestroyAPIView):
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    lookup_field = "id"
    permission_classes = [ObjectOnlyPermissions]

    def get_object(self):
        obj = super().get_object()
        if self.request.user.has_perm('view_hub', obj):
            return obj
        else:
            raise PermissionDenied


class LeafList(generics.ListAPIView):
    serializer_class = LeafSerializer
    permission_classes = [ObjectOnlyPermissions]

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.leaves
        else:
            raise PermissionDenied


class LeafDetail(generics.RetrieveDestroyAPIView):
    serializer_class = LeafSerializer
    lookup_field = "uuid"
    permission_classes = [ObjectOnlyPermissions]

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.leaves
        else:
            raise PermissionDenied

    def put(self, request, **kwargs):
        print(request.data)
        try:
            value = request.data.get('value', '')
            format = request.data.get('format', '')
            device = request.data.get('device', '')
            assert value is not None and format and device
        except (KeyError, AssertionError):
            return JsonResponse({'accepted': False, 'reason': 'Missing one of [device, value, format]'})
        hub = get_object_or_404(Hub, id=kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            leaf = self.get_object()
            if leaf.devices.filter(name=device).exists():
                device = leaf.devices.get(name=device)
                if device.mode == 'OUT':
                    leaf.group.send({'text':json.dumps({'type': 'SET_OUTPUT', 'device': device.name, 'value': value, 'format': format})})
                    return JsonResponse({'accepted': True})
                else:
                    return JsonResponse({'accepted': False, 'reason': f'{device} is not an output device'})
        else:
            raise PermissionDenied


class DatastoreList(generics.ListAPIView):
    serializer_class = DatastoreSerializer

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.datastores
        else:
            raise PermissionDenied

    def post(self, request, format=None, **kwargs):
        try:
            name = request.data.get('name', '')
            value = request.data.get('value', '')
            format = request.data.get('format', '')
            units = request.data.get('units', '')
            assert name and value is not None and format
        except (KeyError, AssertionError):
            return JsonResponse({'accepted': False, 'reason': 'Missing one of [name, value, format]'})
        hub = get_object_or_404(Hub, id=kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            if Datastore.objects.filter(name=name).exists():
                return JsonResponse({'accepted': False, 'reason': 'Datastore with name already exists'})
            value = create_value(format, value, units)
            value.save()
            datastore = Datastore(name=name, _value=value, hub=hub)
            datastore.save()

            hub_group = PermGroup.objects.get(name="hub-" + str(hub.id))

            assign_perm('view_datastore', hub_group, datastore)
            assign_perm('change_datastore', hub_group, datastore)
            assign_perm('delete_datastore', self.request.user, datastore)

            return JsonResponse({'accepted': True})
        else:
            raise PermissionDenied


class DatastoreDetail(generics.RetrieveDestroyAPIView):
    serializer_class = DatastoreSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.datastores
        else:
            raise PermissionDenied

    def put(self, request, **kwargs):
        print(request.data)
        try:
            value = request.data.get('value', '')
            format = request.data.get('format', '')
            assert value is not None and format is not None
        except (KeyError, AssertionError):
            return JsonResponse({'accepted': False, 'reason': 'Missing one of [value, format]'})
        hub = get_object_or_404(Hub, id=kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            datastore = self.get_object()
            datastore.value = value
            return JsonResponse({'accepted': True})
        else:
            raise PermissionDenied


class ConditionList(generics.ListAPIView):
    serializer_class = ConditionSerializer

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.conditions
        else:
            raise PermissionDenied

    def post(self, request, format=None, **kwargs):
        try:
            name = request.data.get('name', '')
            predicate = request.data.get('predicate', '')
            action = request.data.get('action', '')
            assert name and predicate and action
        except (KeyError, AssertionError):
            return JsonResponse({'accepted': False, 'reason': 'Missing one of [name, predicate, action]'})

        hub = get_object_or_404(Hub, id=kwargs['id'])

        if self.request.user.has_perm('view_hub', hub):
            try:
                create_condition(name, predicate, action, hub)
            except SentinelError as e:
                return JsonResponse({'accepted': True, 'reason': str(e)})

            return JsonResponse({'accepted': True})
        else:
            raise PermissionDenied


class ConditionDetail(generics.RetrieveDestroyAPIView):
    serializer_class = ConditionSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.conditions
        else:
            raise PermissionDenied
