from django.shortcuts import render
from hub.models import Leaf, Device, Datastore, Condition, Hub
from hub.serializers import LeafSerializer, ConditionSerializer, DatastoreSerializer, HubSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user
from guardian.models import Group as PermGroup

# Create your views here.
def main(request, id):
    return render(request, "main.html", {'hub': id})


def fake_in(request, id):
    return render(request, "fake_rfid.html", {'hub': id})


def fake_out(request, id):
    return render(request, "fake_door.html", {'hub': id})


def rfid_demo(request, id):
    return render(request, "rfid_demo.html", {'hub': id})


class HubList(generics.ListAPIView):
    serializer_class = HubSerializer

    def get_queryset(self):
        user = self.request.user
        return get_objects_for_user(user, 'view_hub', Hub.objects.all())


class HubDetail(generics.RetrieveAPIView):
    serializer_class = HubSerializer
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        return get_objects_for_user(user, 'view_hub', Hub.objects.all())


class LeafList(generics.ListAPIView):
    serializer_class = LeafSerializer

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.leaves


class LeafDetail(generics.RetrieveAPIView):
    serializer_class = LeafSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.leaves


class DatastoreList(generics.ListAPIView):
    serializer_class = DatastoreSerializer

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.datastores


class DatastoreDetail(generics.RetrieveDestroyAPIView):
    serializer_class = DatastoreSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.datastores


class ConditionList(generics.ListAPIView):
    serializer_class = ConditionSerializer

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.conditions


class ConditionDetail(generics.RetrieveDestroyAPIView):
    serializer_class = ConditionSerializer
    lookup_field = "name"

    def get_queryset(self):
        hub = Hub.objects.get(id=self.kwargs['id'])
        return hub.conditions