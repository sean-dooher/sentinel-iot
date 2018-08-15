import json
import logging
from enum import Enum

from channels import Group
from django.contrib.auth import authenticate

from .models import Hub
from .utils import InvalidLeaf, validate_uuid, InvalidDevice, PermissionDenied, InvalidMessage

logger = logging.getLogger(__name__)


class MessageType(Enum):
    Config = 'CONFIG'
    DeviceStatus = 'DEVICE_STATUS'
    Subscribe = 'SUBSCRIBE'
    Unsubscribe = 'UNSUBSCRIBE'
    DatastoreCreate = 'DATASTORE_CREATE'
    DatastoreDelete = 'DATASTORE_DELETE'
    DatastoreGet = 'DATASTORE_GET'
    DatastoreSet = 'DATASTORE_SET'
    ConditionCreate = 'CONDITION_CREATE'
    ConditionDelete = 'CONDITION_DELETE'
    GetDevice = 'GET_DEVICE'


class Message:
    def __init__(self, data):
        self.data = data

        self.hub = Hub.objects.get(id=data['hub'])
        try:
            self.leaf = self.hub.get_leaf(data['uuid'])
            self.user = self.leaf.get_user()
        except InvalidLeaf as e:
            if self.type != MessageType.Config:
                raise e

    @property
    def type(self):
        return MessageType(self.data['type'])

    @property
    def hub_id(self):
        return self.data['hub']

    def validate(self):
        valid = self.type in MessageType
        if not valid:
            return False
        elif self.type == MessageType.Config:
            valid = valid and self.data['name']
            valid = valid and self.data['model']
            valid = valid and self.data['token']
            valid = valid and self.data['api_version']
        elif self.type == MessageType.DeviceStatus:
            valid = valid and self.data['device']
            valid = valid and self.data['mode']
            valid = valid and self.data['format']
            valid = valid and self.data['value']
        elif self.type == MessageType.Subscribe or self.type == MessageType.Unsubscribe:
            valid = valid and self.data['sub_uuid'] and validate_uuid(self.data['sub_uuid'])
            valid = valid and self.data['sub_device']
        elif self.type == MessageType.DatastoreCreate:
            valid = valid and self.data['name']
            valid = valid and self.data['value']
            valid = valid and self.data['format']
        elif self.type == MessageType.DatastoreGet:
            return valid and self.data['name']
        elif self.type == MessageType.DatastoreSet:
            valid = valid and self.data['name']
            valid = valid and self.data['value']
        elif self.type == MessageType.DatastoreDelete:
            valid = valid and self.data['name']
        elif self.type == MessageType.ConditionCreate:
            valid = valid and self.data['name']
            valid = valid and self.data['predicate']
            valid = valid and self.data['actions']
            if valid and type(self.data['actions']) == list:
                for action in self.data['actions']:
                    valid = valid and self.data['target'] in action
                    valid = valid and self.data['device'] in action
                    valid = valid and self.data['value'] in action
        elif self.type == MessageType.ConditionDelete:
            valid = valid and self.data['name']
        else:
            return False
        return valid and self.data['uuid'] and validate_uuid(self.data['uuid'])

    def reply(self, response):
        pass

    def save_session_info(self, name, value):
        pass

    def register_leaf(self, leaf):
        pass


class MessageV1(Message):
    def __init__(self, message):
        self.session = message.channel_session
        self.reply_channel = message.reply_channel

        try:
            data = json.loads(message.content['text'])
            data['hub'] = message.channel_session['hub']
            super().__init__(data)
        except json.decoder.JSONDecodeError as e:
            logger.error(f"{self.hub_id} -- Invalid Message: JSON Decoding failed")
            raise InvalidMessage(e)
        except InvalidMessage as e:
            logger.error(f"{self.hub_id} -- Invalid Message: {e}")
            raise e
        except (InvalidDevice, InvalidLeaf, PermissionDenied) as e:
            logger.error(f"{self.hub_id} -- {e} in handling {self.type} for {self.data['uuid']}")
            reply = e.get_error_message()
            reply['hub'] = self.hub()
            self.reply(reply)
            raise InvalidMessage(e)

    def save_session_info(self, name, value):
        self.session[name] = value

    def reply(self, response):
        self.reply_channel.send({"text": json.dumps(response)})

    def register_leaf(self, leaf):
        Group(f"{leaf.hub.id}-{leaf.uuid}").add(self.reply_channel)

    def unregister_leaf(self, leaf):
        Group(f"{leaf.hub.id}-{leaf.uuid}").discard(self.reply_channel)