from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Leaf, Subscription, Device, Datastore, Hub
from .models import NOT, AND, OR, XOR, SetAction, Condition, ConditionalSubscription, ChangeAction
from .models import GreaterThanPredicate, LessThanPredicate, EqualPredicate
from .utils import is_valid_message, create_value, InvalidDevice, InvalidPredicate, InvalidLeaf
import json
import logging

logger = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_add(message, id):
    # Accept the connection
    message.channel_session['hub'] = id
    message.reply_channel.send({"accept": True})


@channel_session_user_from_http
def ws_disconnect(message):
    if 'user' in message.channel_session:
        hub = Hub.objects.get(pk=message.channel_session['hub'])
        leaf = hub.get_leaf(message.channel_session['user'])
        leaf.is_connected = False
        leaf.save()
        Group(f"{leaf.hub.id}-{leaf.uuid}").discard(message.reply_channel)


@channel_session_user
def ws_message(message):
    try:
        mess = json.loads(message.content['text'])
        message.content['dict'] = mess
        assert is_valid_message(mess), "required attributes missing from message"
        assert 'hub' in message.channel_session and (mess['type'] == 'CONFIG' or 'user' in message.channel_session)
        if mess['type'] == 'CONFIG':
            return hub_handle_config(message)
        elif mess['type'] == 'NAME':
            # TODO: add name handler
            pass
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
        elif mess['type'] == 'DATASTORE_SET':
            return hub_handle_datastore_set(message)
        elif mess['type'] == 'CONDITION_CREATE':
            return hub_handle_condition_create(message)
        elif mess['type'] == 'CONDITION_DELETE':
            return hub_handle_condition_delete(message)
        else:
            logger.error(f"{message.channel_session['hub']} -- Invalid Message: Unknown type in message")
    except json.decoder.JSONDecodeError:
        logger.error(f"{message.channel_session['hub']} -- Invalid Message: JSON Decoding failed")
        logger.error(mess)
    except AssertionError as e:
        logger.error(f"{message.channel_session['hub']} -- Invalid Message: {e}")
        logger.error(mess)
    except (InvalidDevice, InvalidLeaf) as e:
        leaf = message.channel_session['user']
        logger.error(f"{message.channel_session['hub']} -- {e} in handling {mess['type']} for {leaf}")
        message.reply_channel.send({'text': e.get_error_message()})


def hub_handle_config(message):
    mess = message.content['dict']
    api = mess['api_version']
    uuid = mess['uuid']
    hub = Hub.objects.get(id=message.channel_session['hub'])

    try:
        leaf = hub.get_leaf(uuid)
        leaf.api_version = api
    except InvalidLeaf:
        leaf = Leaf.create_from_message(mess, hub)
        leaf.hub = hub
        leaf.save()

    try:
        User.objects.get(username=uuid)
    except User.DoesNotExist:
        user = User.objects.create_user(username=uuid, password=mess['password'])
        user.save()

    user = authenticate(username=uuid, password=mess['password'])
    if user:
        leaf.is_connected = True
        leaf.save()
        Group(f"{leaf.hub.id}-{leaf.uuid}").add(message.reply_channel)
        message.channel_session['user'] = user.username
        response = {"text": {"type": "CONFIG_COMPLETE", "hub": hub.id, "uuid": uuid}}
        message.reply_channel.send(response)
        leaf.refresh_devices()
        logger.info(f'{hub.id} -- Config received for {leaf.name}')
    else:
        logger.error(f"{hub.id} -- Authentication failed for {uuid}")
        response = {"text": {"type": "CONFIG_FAILED", "hub": hub.id, "uuid": uuid}}
        message.reply_channel.send(response)


def hub_handle_status(message):
    mess = message.content['dict']
    hub = Hub.objects.get(id=message.channel_session['hub'])
    leaf = hub.get_leaf(message.channel_session['user'])
    device_name = mess["device"].lower()

    try:
        device = leaf.get_device(device_name, False)
    except Device.DoesNotExist:
        device = Device.create_from_message(mess, hub)
        device.save()
    device.value = mess['value']
    logger.info(f'{hub.id} -- Status updated: {device}')


def hub_handle_subscribe(message):
    mess = message.content['dict']
    target_uuid = mess['sub_uuid'].lower()
    subscriber_uuid = message.channel_session['user'].lower()
    device = mess['sub_device'].lower()
    hub = Hub.objects.get(id=message.channel_session['hub'])

    # ensure the target exists by trying to access it
    if device == 'leaf':
        hub.get_leaf(target_uuid)
    else:
        hub.get_device(target_uuid, device)

    try:
        hub.subscriptions.get(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device)
        logger.info(f"{hub.id} -- <{subscriber_uuid}> subscribed to <{target_uuid}-{device}>")
    except ObjectDoesNotExist:
        subscription = Subscription(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device, hub=hub)
        subscription.save()


def hub_handle_unsubscribe(message):
    mess = message.content['dict']
    target_uuid = mess['sub_uuid'].lower()
    subscriber_uuid = message.channel_session['user'].lower()
    device = mess['sub_device'].lower()
    hub = Hub.objects.get(id=message.channel_session['hub'])

    # ensure the target exists by trying to access it
    if device == 'leaf':
        hub.get_leaf(target_uuid)
    else:
        hub.get_device(target_uuid, device)

    try:
        subscription = hub.subscriptions.get(subscriber_uuid=subscriber_uuid,
                                             target_uuid=target_uuid, target_device=device)
        subscription.delete()
        logger.info(f"{hub.id} -- <{subscriber_uuid}> unsubscribed from <{target_uuid}-{device}>")
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


def hub_handle_condition_create(message):
    mess = message.content['dict']

    operators = {'AND': AND, 'OR': OR, 'XOR': XOR}
    seen_devices = set()

    hub = Hub.objects.get(id=message.channel_session['hub'])

    def eval_predicates(predicates):
        first = predicates[0]
        if first == 'NOT':
            predicate = eval_predicates(predicates[1])
            not_predicate = NOT(predicate)
            not_predicate.save()
            return not_predicate
        elif type(first) == str and first in operators:
            first_predicate = eval_predicates(predicates[1])
            second_predicate = eval_predicates(predicates[2])
            predicate = operators[first](first=first_predicate, second=second_predicate)
            predicate.save()
            return predicate
        else:
            target_uuid, target_device = predicates[1]
            seen_devices.add((target_uuid, target_device))
            first_value = hub.get_device(target_uuid, target_device)._value

            if type(predicates[2]) != list:
                second_value = create_value(first_value.format, value=predicates[2])
                second_value.save()
            else:
                remote_uuid, remote_device = predicates[2]
                seen_devices.add((remote_uuid, remote_device))
                second_value = hub.get_device(remote_uuid, remote_device)._value

            comparator = first
            if comparator == '=':
                predicate = EqualPredicate(first_value=first_value, second_value=second_value)
            elif comparator == '!=':
                equal = EqualPredicate(first_value=first_value, second_value=second_value)
                equal.save()
                predicate = NOT(predicate=equal)
            elif comparator == '<':
                predicate = LessThanPredicate(first_value=first_value, second_value=second_value)
            elif comparator == '<=':
                greater_than = GreaterThanPredicate(first_value=first_value, second_value=second_value)
                greater_than.save()
                predicate = NOT(predicate=greater_than)
            elif comparator == '>':
                predicate = GreaterThanPredicate(first_value=first_value, second_value=second_value)
            elif comparator == '>=':
                less_than = LessThanPredicate(first_value=first_value, second_value=second_value)
                less_than.save()
                predicate = NOT(predicate=less_than)
            else:
                logger.error(f"{hub.id} -- Invalid predicate comparator: {comparator}")
                raise InvalidPredicate(message['predicates'], mess['name'])
            predicate.save()
            return predicate

    predicate = eval_predicates(mess['predicate'])

    # create action
    target_uuid, target_device = mess['action']['target'], mess['action']['device']
    output_device = hub.get_device(target_uuid, target_device)
    output_format = output_device.format
    if isinstance(output_device, Datastore) or output_device.mode == 'OUT':
        value = create_value(output_format, mess['action']['value'])
        value.save()

        if type(mess['action']['value']) != list:
            value = create_value(output_format, value=mess['action']['value'])
            value.save()
        else:
            remote_uuid, remote_device = mess['action']['value']
            seen_devices.add((remote_uuid, remote_device))
            value = hub.get_device(remote_uuid, remote_device)._value

        if mess['action']['action_type'] == 'SET':
            action = SetAction(target_uuid=target_uuid, target_device=target_device, _value=value)
            action.save()
        elif mess['action']['action_type'] == 'CHANGE':
            action = ChangeAction(target_uuid=target_uuid, target_device=target_device, _value=value)
            action.save()
    else:
        raise InvalidDevice(hub.get_leaf(target_uuid), output_device, InvalidDevice.MODE)

    # save condition, deleting old one if exists
    condition = Condition(name=mess['name'], predicate=predicate, action=action, hub=hub)
    try:
        old_condition = hub.conditions.get(name=mess['name'])
        old_condition.delete()
    except ObjectDoesNotExist:
        pass
    condition.save()
    for target, device in seen_devices:
        cond_sub = ConditionalSubscription(target_uuid=target, target_device=device, condition=condition, hub=hub)
        cond_sub.save()
    logger.info(f"{hub.id} -- {condition.name} condition set up")


def hub_handle_condition_delete(message):
    mess = message.content['dict']
    hub = Hub.objects.get(id=message.channel_session['hub'])

    try:
        condition = hub.conditions.get(name=mess['name'])
        condition.delete()
    except ObjectDoesNotExist:
        logger.error(f"{hub.id} -- tried to delete {mess['name']} condition that does not exist")
