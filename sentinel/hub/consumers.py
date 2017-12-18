from channels import Group
from channels.sessions import channel_session
from django.core.exceptions import ObjectDoesNotExist
from .models import Leaf, Subscription
from .utils import name_hash, is_valid_message
import json
import logging

logger = logging.getLogger(__name__)


@channel_session
def ws_add(message, hub):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    message.channel_session['hub'] = hub

@channel_session
def ws_message(message):
    try:
        mess = json.loads(message.content['text'])
        if 'type' in mess:
            type = mess['type']
            if type == 'CONFIG':
                return ws_handle_config(message, mess)
            elif type == 'DEVICE_STATUS':
                return ws_handle_status(message, mess)
            elif type == 'SUBSCRIBE':
                return ws_handle_subscribe(message, mess)
    except json.decoder.JSONDecodeError:
        logger.error("Invalid Message: JSON Decoding failed")


def ws_handle_config(message, mess):
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


def ws_handle_status(message, mess):
    leaf = Leaf.objects.get(pk=mess['uuid'])
    device_name = mess["device"].lower()
    device_format = mess["format"].lower()
    try:
        device = leaf.get_device(device_name, False)
    except KeyError:
        device = leaf.create_device(device_name, device_format)
    device.update_value(mess)
    logger.info('Status updated: {}'.format(device))


def ws_handle_subscribe(message, mess):
    target_uuid = mess['sub_uuid'].lower()
    subscriber_uuid = mess['uuid'].lower()
    device = mess['sub_device'].lower()
    logger.info("<{}> subscribed to <{}-{}>".format(subscriber_uuid, target_uuid, device))
    try:
        subscriber = Leaf.objects.get(pk=subscriber_uuid)
        target_leaf = Leaf.objects.get(pk=target_uuid)
    except ObjectDoesNotExist:
        return

    try:
        subscription = Subscription.objects.get(subscriber=subscriber, target_leaf=target_leaf, target_device=device)
    except ObjectDoesNotExist:
        subscription = Subscription(subscriber=subscriber, target_leaf=target_leaf, target_device=device)
        subscription.save()


@channel_session
def ws_disconnect(message):
    if 'leaf' in message.channel_session:
        leaf = Leaf.objects.get(pk=message.channel_session['leaf'])
        leaf.isConnected = False
        leaf.save()
        Group(leaf.uuid).discard(message.reply_channel)
    # TODO: Add unsubscribe on disconnect
