from django.shortcuts import render
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hub.models import Leaf, Device, Datastore, Condition
from hub.serializers import LeafSerializer, ConditionSerializer


# Create your views here.
def main(request):
    return render(request, "index.html")


def fake_in(request):
    return render(request, "fake_rfid.html")


def fake_out(request):
    return render(request, "fake_door.html")


def rfid_demo(request):
    return render(request, "rfid_demo.html")


@api_view(['GET'])
def leaf_list(request):
    if request.method == 'GET':
        leaves = Leaf.objects.all()
        serializer = LeafSerializer(leaves, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def leaf_detail(request, uuid):
    try:
        leaf = Leaf.objects.get(uuid=uuid)
    except Leaf.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LeafSerializer(leaf)
        return Response(serializer.data)


@api_view(['GET'])
def datastore_list(request):
    if request.method == 'GET':
        datastores = Datastore.objects.all()
        serializer = LeafSerializer(datastores, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def condition_list(request):
    if request.method == 'GET':
        conditions = Condition.objects.all()
        serializer = ConditionSerializer(conditions, many=True)
        return Response(serializer.data)


@api_view(['GET', 'DELETE'])
def condition_detail(request, name):
    try:
        condition = Condition.objects.get(name=name)
    except Condition.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ConditionSerializer(condition)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        condition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)