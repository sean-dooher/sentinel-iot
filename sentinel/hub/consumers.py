from channels import Group, Channel
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from channels.auth import channel_session_user, channel_session_user_from_http
from django.core.exceptions import ObjectDoesNotExist
from .models import Leaf, Subscription, Device
from .utils import is_valid_message
import json
import logging

logger = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})


@channel_session_user_from_http
def ws_disconnect(message):
    if 'leaf' in message.channel_session:
        leaf = Leaf.objects.get(pk=message.channel_session['leaf'])
        leaf.isConnected = False
        leaf.save()
        Group(leaf.uuid).discard(message.reply_channel)


@channel_session_user
def ws_message(message):
    try:
        mess = json.loads(message.content['text'])
        message.content['dict'] = mess
        if mess['type'] == 'CONFIG':
            return hub_handle_config(message)
        elif mess['type'] == 'DEVICE_STATUS':
            return hub_handle_status(message)
        elif mess['type'] == 'SUBSCRIBE':
            return hub_handle_subscribe(message)
        elif mess['type'] == 'UNSUBSCRIBE':
            return hub_handle_unsubscribe(message)
        elif mess['type'] == 'DATASTORE_CREATE':
            return hub_handle_datastore_create(message)
        elif mess['type'] == 'DATASTORE_GET':
            return hub_handle_datastore_get(message)
        elif message['type'] == 'DATSTORE_SET':
            return hub_handle_datastore_set(message)
    except json.decoder.JSONDecodeError:
        logger.error("Invalid Message: JSON Decoding failed")


def hub_handle_config(message):
    mess = message.content['dict']
    api = mess['api_version']
    uuid = mess['uuid']

    try:
        leaf = Leaf.objects.get(pk=uuid)
        leaf.api_version = api
    except ObjectDoesNotExist:
        leaf = Leaf.create_from_message(mess)
    leaf.save()
    leaf.refresh_devices()
    Group(uuid).add(message.reply_channel)
    message.channel_session['leaf'] = uuid
    response = {"text": json.dumps({"type": "CONFIG_COMPLETE", "hub_id": 1, "uuid": uuid})}
    message.reply_channel.send(response)
    logger.info('Config received for {}'.format(leaf.name))


def hub_handle_status(message):
    mess = message.content['dict']
    leaf = Leaf.objects.get(pk=mess['uuid'])
    device_name = mess["device"].lower()
    device_format = mess["format"].lower()
    try:
        device = leaf.get_device(device_name, False)
    except ObjectDoesNotExist:
        device = Device.create_from_message(mess)
    device.value = mess['value']
    logger.info('Status updated: {}'.format(device))


def hub_handle_subscribe(message):
    mess = message.content['dict']
    target_uuid = mess['sub_uuid'].lower()
    subscriber_uuid = mess['uuid'].lower()
    device = mess['sub_device'].lower()
    logger.info("<{}> subscribed to <{}-{}>".format(subscriber_uuid, target_uuid, device))
    try:
        Leaf.objects.get(pk=subscriber_uuid)
        if not target_uuid == 'datastore':
            Leaf.objects.get(pk=target_uuid)
    except ObjectDoesNotExist:
        return

    try:
        Subscription.objects.get(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device)
    except ObjectDoesNotExist:
        subscription = Subscription(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device)
        subscription.save()


def hub_handle_unsubscribe(message):
    mess = message.content['dict']
    target_uuid = mess['sub_uuid'].lower()
    subscriber_uuid = mess['uuid'].lower()
    device = mess['sub_device'].lower()
    logger.info("<{}> subscribed to <{}-{}>".format(subscriber_uuid, target_uuid, device))
    try:
        Leaf.objects.get(pk=subscriber_uuid)
        if not target_uuid == 'datastore':
            Leaf.objects.get(pk=target_uuid)
    except ObjectDoesNotExist:
        return

    try:
        subscription = Subscription.objects.get(subscriber_uuid=subscriber_uuid,
                                                target_uuid=target_uuid, target_device=device)
        subscription.delete()
    except ObjectDoesNotExist:
        return


def hub_handle_datastore_create(message):
    mess = message.content['dict']
    pass


def hub_handle_datastore_get(message):
    mess = message.content['dict']
    pass


def hub_handle_datastore_set(message):
    mess = message.content['dict']
    pass