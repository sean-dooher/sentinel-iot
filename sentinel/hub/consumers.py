from channels import Group, Channel
from channels.sessions import channel_session
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
    Channel("hub.connect").send(message)


@channel_session_user_from_http
def hub_add(message):
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
        mess['reply_channel'] = message.content['reply_channel']
        Channel("hub.receive").send(mess)
    except json.decoder.JSONDecodeError:
        logger.error("Invalid Message: JSON Decoding failed")

@channel_session_user
def hub_handle_config(message):
    api = message['api_version']
    uuid = message['uuid']

    try:
        leaf = Leaf.objects.get(pk=uuid)
        leaf.api_version = api
    except ObjectDoesNotExist:
        leaf = Leaf.create_from_message(message)
    leaf.save()
    leaf.refresh_devices()
    message.user.login(username=uuid, password="")
    Group(uuid).add(message.reply_channel)
    message.channel_session['leaf'] = uuid
    response = {"text": json.dumps({"type": "CONFIG_COMPLETE", "hub_id": 1, "uuid": uuid})}
    message.reply_channel.send(response)
    logger.info('Config received for {}'.format(leaf.name))


@channel_session_user
def hub_handle_status(message):
    leaf = Leaf.objects.get(pk=message['uuid'])
    device_name = message["device"].lower()
    device_format = message["format"].lower()
    try:
        device = leaf.get_device(device_name, False)
    except ObjectDoesNotExist:
        device = Device.create_from_message(message)
    device.value = message['value']
    logger.info('Status updated: {}'.format(device))


@channel_session_user
def hub_handle_subscribe(message):
    target_uuid = message['sub_uuid'].lower()
    subscriber_uuid = message['uuid'].lower()
    device = message['sub_device'].lower()
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


@channel_session_user
def hub_handle_unsubscribe(message):
    target_uuid = message['sub_uuid'].lower()
    subscriber_uuid = message['uuid'].lower()
    device = message['sub_device'].lower()
    logger.info("<{}> subscribed to <{}-{}>".format(subscriber_uuid, target_uuid, device))
    try:
        Leaf.objects.get(pk=subscriber_uuid)
        if not target_uuid == 'datastore':
            Leaf.objects.get(pk=target_uuid)
    except ObjectDoesNotExist:
        return

    try:
        subscription = Subscription.objects.get(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device)
        subscription.delete()
    except ObjectDoesNotExist:
        return


@channel_session_user
def hub_handle_datastore_create(message):
    pass


@channel_session_user
def hub_handle_datastore_get(message):
    pass


@channel_session_user
def hub_handle_datastore_set(message):
    pass