from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from polymorphic.models import PolymorphicModel
from channels import Group
import json


class Value(PolymorphicModel):
    value = None

    def __repr__(self):
        return str(self.value)


class StringValue(Value):
    value = models.CharField(max_length=250)

    @property
    def format(self):
        return "string"


class NumberValue(Value):
    value = models.DecimalField(max_digits=15, decimal_places=4)

    @property
    def format(self):
        return "number"


class UnitValue(Value):
    value = models.DecimalField(max_digits=15, decimal_places=4)
    units = models.CharField(max_length=10)

    @property
    def format(self):
        return "number+units"

    def __repr__(self):
        return "{}{}".format(self.value, self.units)


class BooleanValue(Value):
    value = models.BooleanField()

    @property
    def format(self):
        return "bool"


class Leaf(models.Model):
    # TODO: integrate with authentication, user
    hub_id = 1
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    uuid = models.CharField(primary_key=True, max_length=36, unique=True)
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

    def send_subscriber_update(self, device):
        seen_devices = set()
        message = device.status_update_dict

        subscriptions = Subscription.objects.filter(target_uuid=self.uuid)
        for subscription in subscriptions.filter(target_device=device.name):
            seen_devices.add(subscription.subscriber_uuid)
            subscription.handle_update(self.uuid, device.name, message)
        # send messages to whole leaf subscribers
        for subscription in subscriptions.filter(target_device="leaf"):
            if subscription.subscriber_uuid not in seen_devices:
                subscription.handle_update(self.uuid, 'leaf', message)

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


class Device(models.Model):
    name = models.CharField(max_length=100)
    leaf = models.ForeignKey(Leaf, related_name='devices', on_delete=models.CASCADE)
    is_input = models.BooleanField(default=True)
    _value = models.OneToOneField(Value, on_delete=models.CASCADE, related_name="device")

    @property
    def value(self):
        return self._value.value

    @value.setter
    def value(self, new_value):
        self._value.value = new_value
        self._value.save()
        self.leaf.send_subscriber_update(self)

    @property
    def status_update_dict(self):
        status_update = {
            'type': 'DEVICE_STATUS',
            'uuid': self.leaf.uuid,
            'device': self.name,
            'value': self.value,
            'format': self.format,
        }
        if self.format == 'units':
            status_update['units'] = self._value.units
        return status_update

    def refresh_from_db(self, using=None, fields=None):
        self._value.refresh_from_db()
        return super().refresh_from_db(using=using, fields=fields)

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

        is_input = message['mode'].upper() == 'IN'

        format = message['format'].lower()
        if format == 'number':
            value = NumberValue(value=message['value'])
        elif format == 'number+units':
            value = UnitValue(value=message['value'], units=message['units'])
        elif format == 'bool':
            value = BooleanValue(value=message['value'])
        else:
            value = StringValue(value=message['value'])
        value.save()

        device = Device(name=message['device'], _value=value, is_input=is_input, leaf=leaf)
        device.save()
        return device

    @property
    def format(self):
        return self._value.format

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "<Device name:{}, value: {}>".format(self.name, repr(self.value))


class Subscription(PolymorphicModel):
    subscriber_uuid = models.CharField(max_length=36, blank=True, null=True)
    target_uuid = models.CharField(max_length=36)
    target_device = models.CharField(max_length=100)

    def handle_update(self, uuid, device, message):
        sub_message = {'type': 'SUBSCRIPTION_UPDATE',
                       'sub_uuid': uuid,
                       'sub_device': device,
                       'message': message}
        Group(self.subscriber_uuid).send({'text': json.dumps(sub_message)})


class Datastore(models.Model):
    _value = models.OneToOneField(Value, on_delete=models.CASCADE, related_name="datastore")
    name = models.CharField(max_length=100)

    @property
    def format(self):
        return self._value.format

    @property
    def value(self):
        return self._value.value

    @value.setter
    def value(self, new_value):
        self._value.value = new_value
        self._value.save()
        message = {
            'type': 'DEVICE_STATUS',
            'value': self.value,
            'format': self.format,
            'uuid': 'datastore',
            'device': self.name
        }
        subscriptions = Subscription.objects.filter(target_uuid="datastore", device=self.name)
        for subscription in subscriptions:
            subscription.handle_update("datastore", self.name, message)

    def refresh_from_db(self, using=None, fields=None):
        self._value.refresh_from_db()
        return super().refresh_from_db(using=using, fields=fields)


class Predicate(PolymorphicModel):
    def evaluate(self):
        return True


class NOT(Predicate):
    predicate = models.ForeignKey(Predicate, on_delete=models.CASCADE, related_name="not+")

    def evaluate(self):
        return not self.predicate.evaluate()

    def delete(self, *args, **kwargs):
        self.predicate.delete()
        super().delete(*args, **kwargs)


class Bivariate(Predicate):
    first = models.ForeignKey(Predicate, on_delete=models.CASCADE, related_name="first_predicate")
    second = models.ForeignKey(Predicate, on_delete=models.CASCADE, related_name="second_predicate")

    def operator(self, x, y):
        return False

    def evaluate(self):
        return self.operator(self.first, self.second)

    def delete(self, *args, **kwargs):
        self.first.delete()
        self.second.delete()
        super().delete(*args, **kwargs)


class AND(Bivariate):
    def operator(self, x, y):
        return x.evaluate() and y.evaluate()


class OR(Bivariate):
    def operator(self, x, y):
        return x.evaluate() or y.evaluate()


class XOR(Bivariate):
    def operator(self, x, y):
        x = x.evaluate()
        y = y.evaluate()
        return x ^ y


class ComparatorPredicate(Predicate):
    first_value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name="first")
    second_value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name="second")

    def save(self, *args, **kwargs):
        if self.first_value.format != self.second_value.format:
            raise TypeError("Type format mismatch. {} does not equal {}".format(self.first_value.format,
                                                                                self.second_value.format))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.second_value.device  # see if the value is a literal or device value
        except ObjectDoesNotExist:
            self.second_value.delete()  # delete the value if it's a literal
        super().delete(*args, **kwargs)


class EqualPredicate(ComparatorPredicate):
    def evaluate(self):
        return self.first_value.value == self.second_value.value


class LessThanPredicate(ComparatorPredicate):
    def evaluate(self):
        return self.first_value.value < self.second_value.value


class GreaterThanPredicate(ComparatorPredicate):
    def evaluate(self):
        return self.first_value.value > self.second_value.value


class Action(PolymorphicModel):
    def run(self):
        pass


class SetAction(Action):
    target_uuid = models.CharField(max_length=36)
    target_device = models.CharField(max_length=36)
    value = models.OneToOneField(Value, on_delete=models.CASCADE)

    def run(self):
        message = {'type': 'SET_OUTPUT',
                   'uuid': self.target_uuid,
                   'device': self.target_device,
                   'value': self.value.value,
                   'format': self.value.format}
        Group(self.target_uuid).send({'text': message})


class ChangeAction(Action):
    target_uuid = models.CharField(max_length=36)
    target_device = models.CharField(max_length=36)
    value = models.OneToOneField(Value, on_delete=models.CASCADE)

    def run(self):
        message = {'type': 'CHANGE_OUTPUT',
                   'uuid': self.target_uuid,
                   'device': self.target_device,
                   'value': self.value.value,
                   'format': self.value.format}
        Group(self.target_uuid).send({'text': message})


class Condition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    predicate = models.OneToOneField(Predicate, on_delete=models.CASCADE, related_name="condition")
    action = models.OneToOneField(Action, on_delete=models.CASCADE, related_name="condition")

    def execute(self):
        if self.predicate.evaluate():
            self.action.run()

    def delete(self, *args, **kwargs):
        self.predicate.delete()
        self.action.delete()
        super().delete(*args, **kwargs)


class ConditionalSubscription(Subscription):
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)

    def handle_update(self, uuid, device, message):
        if message['type'] == 'DEVICE_STATUS':
            self.condition.execute()
