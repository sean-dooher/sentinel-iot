from channels import Group
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
    # Group("chat").send({
    #     "text": message.content['text'],
    # })
    # print(message.content['text'])
    mess = json.loads(message.content['text'])
    if('type' in mess and mess['type'] == 'RESPONSE'):
    	print(mess['data'])
    elif('type' in mess and mess['type'] == 'CONFIG'):
    	message.channel_session['interface'] = mess['interface']
    	message.channel_session['model'] = mess['model']
    	message.channel_session['serial'] = message['serial']
    	message.channel_session['name'] = message['name']

@channel_session
def ws_disconnect(message):
    Group(message.channel_session['group']).discard(message.reply_channel)