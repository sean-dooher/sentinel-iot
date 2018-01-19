from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from hub.models import Leaf, Device, Datastore, Condition, Hub
from hub.serializers import LeafSerializer, ConditionSerializer, DatastoreSerializer, HubSerializer
from .utils import validate_uuid
from rest_framework import generics
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from guardian.models import Group as PermGroup
import secrets, json


def fake_in(request, id):
    return render(request, "fake_rfid.html", {"hub": id})


def fake_out(request, id):
    return render(request, "fake_door.html", {"hub": id})


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

    def get_object(self):
        obj = super().get_object()
        if self.request.user.has_perm('view_hub', obj):
            return obj
        else:
            raise PermissionDenied


class LeafList(generics.ListAPIView):
    serializer_class = LeafSerializer

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.leaves
        else:
            raise PermissionDenied


class LeafDetail(generics.RetrieveAPIView):
    serializer_class = LeafSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.leaves
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


class DatastoreDetail(generics.RetrieveDestroyAPIView):
    serializer_class = DatastoreSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.datastores
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


class ConditionDetail(generics.RetrieveDestroyAPIView):
    serializer_class = ConditionSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = get_object_or_404(Hub, id=self.kwargs['id'])
        if self.request.user.has_perm('view_hub', hub):
            return hub.conditions
        else:
            raise PermissionDenied
