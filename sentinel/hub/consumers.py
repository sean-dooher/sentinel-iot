from channels import Group
from channels.sessions import channel_session
from django.core.exceptions import ObjectDoesNotExist
from .models import Leaf
from utils import *
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
			type = mess['type']
			if type == 'CONFIG':
			   return ws_handle_config(message, mess)
			elif type == 'DEVICE_STATUS':
				return ws_handle_status(message, mess)
	except json.decoder.JSONDecodeError:
		print("invalid message")

def ws_handle_config(message, mess):
	mess = json.loads(message.content['text'])

	if not is_valid_message(mess, 'CONFIG'):
		reply = {"text":json.dumps({"type":"INVALID_CONFIG"})}
		message.reply_channel.send(reply)
		return

	model = mess['model']
	uuid = mess['uuid']
	name = mess['name']
	api = mess['api_version']

	try:
		leaf = Leaf.objects.get(pk=uuid)
		leaf.api_version = api
	except ObjectDoesNotExist:
		leaf = Leaf(name=name, api_version=api, uuid=uuid, model=model)
	leaf.save()
	leaf.refresh_devices()
	Group(uuid).add(message.reply_channel)
	message.channel_session['leaf'] = uuid
	response = {"text":json.dumps({"type":"CONFIG_COMPLETE", "hub_id":1, "uuid":uuid})}
	message.reply_channel.send(response)
	print('config recieved')

def ws_handle_status(message, mess):
	if not is_valid_message(mess, 'DEVICE'):
		reply = {"text":json.dumps({"type":"INVALID_MESSAGE", "message": mess})}
		message.reply_channel.send(reply)
		return

	if 'leaf' not in message.channel_session:
		return

	leaf = Leaf.objects.get(pk=message.channel_session['leaf'])
	device_name = mess["device"]
	device_format = mess["format"]
	try:
		device = leaf.get_devices()[device_name]
	except KeyError:
		device = leaf.create_device(device_name, device_format)
	device.update_value(mess)
	device.save()
	print('status updated: {}'.format(device))

@channel_session
def ws_disconnect(message):
	if 'leaf' in message.channel_session:
		leaf = Leaf.objects.get(pk=message.channel_session['leaf'])
		leaf.isConnected = False
		Group(leaf.uuid).discard(message.reply_channel)
	Group(message.channel_session['group']).discard(message.reply_channel)