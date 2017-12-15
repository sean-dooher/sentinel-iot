from channels import Group
from channels.sessions import channel_session
from django.core.exceptions import ObjectDoesNotExist
from .models import Leaf
from .utils import *
import json
# Connected to websocket.connect
@channel_session
def ws_add(message, group):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    message.channel_session['group'] = group
    Group(group).add(message.reply_channel)

@channel_session
def ws_message(message):
    try:
        mess = json.loads(message.content['text'])
        if 'type' in mess:
            if 'uuid' in mess:
                sub_message = {"type":"SUBSCRIBER_UPDATE","hub_id":1, "message":message.content['text']}
                response = {"text":json.dumps(sub_message)}
                Group(mess['uuid'] + "-sub").send(response)

            type = mess['type']
            if type == 'CONFIG':
                return ws_handle_config(message, mess)
            elif type == 'DEVICE_STATUS':
                return ws_handle_status(message, mess)
            elif type == 'SUBSCRIBE':
                return ws_handle_subscribe(message, mess)
    except json.decoder.JSONDecodeError:
        print("invalid message")


def ws_handle_config(message, mess):
    if not is_valid_message(mess, 'CONFIG'):
        reply = {"text":json.dumps({"type":"INVALID_CONFIG"})}
        return
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
    response = {"text":json.dumps({"type":"CONFIG_COMPLETE", "hub_id":1, "uuid":uuid})}
    message.reply_channel.send(response)
    print('config received')


def ws_handle_status(mess):
    if not is_valid_message(mess, 'DEVICE_STATUS'):
        reply = {"text": json.dumps({"type": "INVALID_MESSAGE", "message": mess})}
        message.reply_channel.send(reply)
        return

    leaf = Leaf.objects.get(pk=mess['uuid'])
    device_name = mess["device"]
    device_format = mess["format"]
    try:
        device = leaf.get_device(device_name, False)
    except KeyError:
        device = leaf.create_device(device_name, device_format)
    device.update_value(mess)
    device.save()
    print('status updated: {}'.format(device))


def ws_handle_subscribe(message, mess):
    if not is_valid_message(mess, 'SUBSCRIBE'):
        reply = {"text":json.dumps({"type":"INVALID_MESSAGE", "message": mess})}
        message.reply_channel.send(reply)
        return
    uuid = mess['sub_uuid']
    print("<{}> subscribed to <{}>".format(mess["uuid"], uuid))
    Group(uuid + "-sub").add(message.reply_channel)


@channel_session
def ws_disconnect(message):
    if 'leaf' in message.channel_session:
        leaf = Leaf.objects.get(pk=message.channel_session['leaf'])
        leaf.isConnected = False
        Group(leaf.uuid).discard(message.reply_channel)
    Group(message.channel_session['group']).discard(message.reply_channel)