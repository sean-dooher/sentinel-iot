from django.shortcuts import render, get_object_or_404
from hub.models import Leaf, Device, Datastore, Condition, Hub
from hub.serializers import LeafSerializer, ConditionSerializer, DatastoreSerializer, HubSerializer
from rest_framework import generics
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from guardian.models import Group as PermGroup


def register_leaf(request, id):
    hub = get_object_or_404(Hub, id=id)
    if request.user.has_perm('delete_hub', hub):
        print("True")


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
