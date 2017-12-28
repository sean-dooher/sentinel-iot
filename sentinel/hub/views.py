from django.shortcuts import render
from hub.models import Leaf, Device, Datastore, Condition
from hub.serializers import LeafSerializer, ConditionSerializer, DatastoreSerializer
from rest_framework import generics


# Create your views here.
def main(request):
    return render(request, "index.html")


def fake_in(request):
    return render(request, "fake_rfid.html")


def fake_out(request):
    return render(request, "fake_door.html")


def rfid_demo(request):
    return render(request, "rfid_demo.html")


class LeafList(generics.ListAPIView):
    queryset = Leaf.objects.all()
    serializer_class = LeafSerializer


class LeafDetail(generics.RetrieveAPIView):
    queryset = Leaf.objects.all()
    serializer_class = LeafSerializer
    lookup_field = "uuid"


class DatastoreList(generics.ListAPIView):
    queryset = Datastore.objects.all()
    serializer_class = DatastoreSerializer


class DatastoreDetail(generics.RetrieveDestroyAPIView):
    queryset = Datastore.objects.all()
    serializer_class = DatastoreSerializer
    lookup_field = "name"


class ConditionList(generics.ListAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer


class ConditionDetail(generics.RetrieveDestroyAPIView):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    lookup_field = "name"
