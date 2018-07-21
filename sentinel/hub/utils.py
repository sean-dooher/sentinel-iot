from .models import Leaf, NumberValue, UnitValue, BooleanValue, StringValue
from django.contrib.auth.models import User
import re
uuid_pattern = re.compile('[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z', re.I)


def is_valid_message(message):
    valid = 'type' in message
    if not valid:
        return False
    elif message['type'] == 'CONFIG':
        valid = valid and 'name' in message
        valid = valid and 'model' in message
        valid = valid and 'token' in message
        valid = valid and 'api_version' in message
    elif message['type'] == 'DEVICE_STATUS':
        valid = valid and 'device' in message
        valid = valid and 'mode' in message
        valid = valid and 'format' in message
        valid = valid and 'value' in message
    elif message['type'] == 'SUBSCRIBE' or message['type'] == 'UNSUBSCRIBE':
        valid = valid and 'sub_uuid' in message and validate_uuid(message['sub_uuid'])
        valid = valid and 'sub_device' in message
    elif message['type'] == 'DATASTORE_CREATE':
        valid = valid and 'name' in message
        valid = valid and 'value' in message
        valid = valid and 'format' in message
    elif message['type'] == 'DATASTORE_DELETE':
        valid = valid and 'name' in message
    elif message['type'] == 'DATASTORE_GET':
        return valid and 'name' in message
    elif message['type'] == 'DATASTORE_SET':
        valid = valid and 'name' in message
        valid = valid and 'value' in message
    elif message['type'] == 'DATASTORE_DELETE':
        valid = valid and 'name' in message
    elif message['type'] == 'CONDITION_CREATE':
        valid = valid and 'name' in message
        valid = valid and 'predicate' in message
        valid = valid and 'actions' in message
        if valid and type(message['actions']) == list:
            for action in message['actions']:
                valid = valid and 'target' in action
                valid = valid and 'device' in action
                valid = valid and 'value' in action
    elif message['type'] == 'CONDITION_DELETE':
        valid = valid and 'name' in message
    else:
        return False
    return valid and 'uuid' in message and validate_uuid(message['uuid'])


def validate_uuid(uuid):
    uuid = uuid.replace("-", "").lower()
    return re.match(uuid_pattern, uuid) or uuid == 'datastore'


def disconnect_all():
    for leaf in Leaf.objects.all():
        leaf.is_connected = False
        leaf.save()


def create_value(format, value, units=None):
    if format == 'number':
        return NumberValue(value=value)
    elif format == 'number+units':
        return UnitValue(value=value, units=units)
    elif format == 'bool':
        return BooleanValue(value=value)
    else:
        return StringValue(value=value)


def get_user(uuid, hub):
    return User.objects.get(username=f"{hub}-{uuid}")
