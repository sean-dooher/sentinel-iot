from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from polymorphic.models import PolymorphicModel
from channels import Group
import json


class Leaf(models.Model):
    hub_id = 1
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    uuid = models.CharField(primary_key=True, max_length=36)
    api_version = models.CharField(max_length=10, default="0.1.0")
    isConnected = models.BooleanField(default=True)

    def set_name(self, name):
        message = self.message_template
        message["type"] = "SET_NAME"
        message["name"] = name
        self.send_message(message)

    def set_option(self, device, option, value):
        message = self.message_template
        message["type"] = "SET_OPTION"
        message["device"] = device
        message["option"] = option
        message["value"] = value
        self.send_message(message)

    def set_output(self, device, value):
        message = self.message_template
        message["type"] = "SET_OUTPUT"
        message["device"] = device
        message["value"] = value
        self.send_message(message)

    def get_option(self, device, option, update=True):
        if update:
            self.refresh_option(device, option)
        # TODO: Replace following code with real code, add option
        return self.get_device(device, update=False).option_set.filter(name=option)

    def get_options(self, device, update=True):
        if update:
            self.refresh_options()
        return self.get_device(device, update=False).option_set.all()

    def get_device(self, device, update=True):
        if update:
            self.refresh_device(device)
        return self.devices.get(name=device)

    def get_devices(self, update=True):
        if update:
            self.refresh_devices()

        devices = {}
        for device in self.devices.all():
                devices[device.name] = device

        return devices

    def get_name(self):
        return self.name

    def refresh_devices(self):
        message = self.message_template
        message["type"] = "LIST_DEVICES"
        self.send_message(message)

    def refresh_name(self):
        message = self.message_template
        message["type"] = "GET_NAME"
        self.send_message(message)

    def refresh_options(self):
        message = self.message_template
        message["type"] = "LIST_OPTIONS"
        self.send_message(message)

    def refresh_device(self, device):
        message = self.message_template
        message["type"] = "GET_DEVICE"
        message["device"] = device
        self.send_message(message)

    def refresh_option(self, device, option):
        message = self.message_template
        message["type"] = "GET_OPTION"
        message["option"] = option
        message["device"] = device
        self.send_message(message)

    def send_message(self, message):
        message = {"text": json.dumps(message)}
        Group(self.uuid).send(message)

    def create_device(self, device_name, format):
        if format == 'bool':
            device = BooleanDevice(name=device_name, leaf=self, value=False)
        elif format == 'number+units':
            device = UnitDevice(name=device_name, leaf=self, value=0, units="None")
        elif format == 'number':
            device = NumberDevice(name=device_name, leaf=self, value=0)
        else:
            # treat unknown formats as strings per API
            device = StringDevice(name=device_name, leaf=self, value="")
        return device

    def send_subscriber_update(self, device):
        seen_devices = set()
        status = {'type': 'SUBSCRIPTION_UPDATE',
                  'sub_uuid': self.uuid,
                  'sub_device': device.name,
                  'message': device.status_update_dict}

        message = {'text': json.dumps(status)}
        subscriptions = Subscription.objects.filter(target_uuid=self.uuid)
        for subscription in subscriptions.filter(target_device=device.name):
            seen_devices.add(subscription.subscriber_uuid)
            Group(subscription.subscriber_uuid).send(message)
        # send messages to whole leaf subscribers
        status['sub_device'] = 'leaf'
        message = {'text': json.dumps(status)}
        for subscription in subscriptions.filter(target_device="leaf"):
            if subscription.subscriber_uuid not in seen_devices:
                Group(subscription.subscriber_uuid).send(message)

    @property
    def message_template(self):
        return {"uuid": self.uuid, "hub_id": self.hub_id}

    def __repr__(self):
        return "Leaf <name: {}, uuid:{}>".format(self.name, self.uuid)

    def __str__(self):
        return repr(self)

    @classmethod
    def create_from_message(cls, message):
        model = message['model']
        name = message['name']
        api = message['api_version']
        uuid = message['uuid']
        leaf = cls(name=name, model=model, uuid=uuid, api_version=api)
        leaf.save()
        return leaf


class Device(PolymorphicModel):
    name = models.CharField(max_length=100)
    leaf = models.ForeignKey(Leaf, related_name='devices', on_delete=models.CASCADE)
    is_input = models.BooleanField(default=True)

    def update_value(self, message):
        self.value = message['value']
        self.leaf.send_subscriber_update(self)
        self.save()

    @property
    def status_update_dict(self):
        status_update = {
            'type': 'DEVICE_STATUS',
            'uuid': self.leaf.uuid,
            'device': self.name,
            'value': self.value,
            'format': self.format,
        }
        return status_update

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Device <name: {}>".format(self.name)

    @staticmethod
    def create_from_message(message, uuid=None):
        try:
            if not uuid:
                uuid = message['uuid']
            leaf = Leaf.objects.get(pk=uuid)
        except ObjectDoesNotExist:
            return
        except KeyError:
            return

        format = message['format']
        if format == 'number':
            device = NumberDevice(name=message['name'], value=message['value'], leaf=leaf)
        elif format == 'number+units':
            device = UnitDevice(name=message['name'], value=message['value'], leaf=leaf)
        elif format == 'bool':
            device = BooleanDevice(name=message['name'], value=message['value'], leaf=leaf)
        else:
            device = StringDevice(name=message['name'], value=message['value'], leaf=leaf)
        device.save()
        return device

    @staticmethod
    def create_from_device_list(message):
        uuid = message['uuid']
        for device in message['devices']:
            Device.create_from_message(device, uuid)

    @property
    def format(self):
        return "Normal"


class StringDevice(Device):
    value = models.CharField(max_length=250)

    @property
    def format(self):
        return "string"

    def __repr__(self):
        return "StringDevice <name:{}, value: {}>".format(self.name, self.value)


class BooleanDevice(Device):
    value = models.BooleanField()

    @property
    def format(self):
        return "bool"

    def __repr__(self):
        return "BooleanDevice <name:{}, value: {}>".format(self.name, self.value)


class NumberDevice(Device):
    value = models.DecimalField(max_digits=15, decimal_places=4)

    @property
    def format(self):
        return "number"

    def __repr__(self):
        return "NumberDevice <name:{}, value: {}>".format(self.name, self.value)


class UnitDevice(Device):
    value = models.DecimalField(max_digits=15, decimal_places=4)
    units = models.CharField(max_length=10)

    def update_value(self, message):
        self.units = message["units"]
        super().update_value(message)

    @property
    def format(self):
        return "number+units"

    @property
    def status_update_dict(self):
        status = super().status_update_dict
        status['units'] = self.units
        return status

    def __repr__(self):
        return "UnitDevice <name:{}, value: {}>".format(self.name, self.value)

class Subscription(models.Model):
    subscriber_uuid = models.CharField(max_length=36)
    target_uuid = models.CharField(max_length=36)
    target_device = models.CharField(max_length=100)

class DatastoreValue(PolymorphicModel):
    name = models.CharField(max_length=30)
