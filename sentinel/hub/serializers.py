from rest_framework import serializers
from .models import Leaf, Device, Condition, Datastore, Action, SetAction, ChangeAction
from collections import OrderedDict


class NonNullSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Here we filter the null values and creates a new dictionary
        # We use OrderedDict like in original method
        ret = OrderedDict(list(filter(lambda x: x[1] is not None, ret.items())))
        return ret


class ValueSerializer(NonNullSerializer):
    value = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()

    def get_value(self, obj):
        if obj.format in ['number', 'number+units']:
            return float(obj._value.value)
        else:
            return obj._value.value

    def get_units(self, obj):
        if obj.format == 'number+units':
            return obj._value.units
        else:
            return None


class DeviceSerializer(ValueSerializer):
    class Meta:
        model = Device
        fields = ('name', 'format', 'value', 'units')


class LeafSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = Leaf
        fields = ('uuid', 'name', 'model', 'api_version', 'is_connected', 'devices')

    def create(self, validated_data):
        device_data = validated_data.pop('devices')
        leaf = Leaf.objects.create(**validated_data)
        for device in device_data:
            Device.objects.create(leaf=leaf, **device)
        return leaf


class ActionSerializer(ValueSerializer):
    target = serializers.SerializerMethodField()
    device = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = ('action_type', 'target', 'device', 'format', 'value', 'units')

    def get_target(self, obj):
        return obj.target_uuid

    def get_device(self, obj):
        return obj.target_device


class ConditionSerializer(serializers.ModelSerializer):
    predicate = serializers.SerializerMethodField()
    action = ActionSerializer()

    class Meta:
        model = Condition
        fields = ('name', 'predicate', 'action')

    def get_predicate(self, obj):
        return str(obj.predicate.to_representation())


class DatastoreSerializer(ValueSerializer):
    class Meta:
        model = Datastore
        fields = ('name', 'format', 'value', 'units')

