import json
import logging

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import Group as PermGroup

from .messages import MessageType, MessageV1, Message
from .models import Leaf, Subscription, Device, Datastore, Hub
from .models import NOT, AND, OR, XOR, SetAction, Condition, ConditionalSubscription, ChangeAction
from .models import GreaterThanPredicate, LessThanPredicate, EqualPredicate
from .utils import create_value, get_user, InvalidDevice, InvalidPredicate
from .utils import InvalidLeaf, PermissionDenied, InvalidMessage

logger = logging.getLogger(__name__)


def handle(message):
    try:
        if not message.validate():
            raise InvalidMessage(message)
        if message.type == MessageType.Config:
            return hub_handle_config(message)
        elif message.type == MessageType.DeviceStatus:
            return hub_handle_status(message)
        elif message.type == MessageType.Subscribe:
            return hub_handle_subscribe(message)
        elif message.type == MessageType.Unsubscribe:
            return hub_handle_unsubscribe(message)
        elif message.type == MessageType.DatastoreCreate:
            return hub_handle_datastore_create(message)
        elif message.type == MessageType.DatastoreDelete:
            return hub_handle_datastore_delete(message)
        elif message.type == MessageType.DatastoreGet:
            return hub_handle_datastore_get(message)
        elif message.type == MessageType.DatastoreSet:
            return hub_handle_datastore_set(message)
        elif message.type == MessageType.ConditionCreate:
            return hub_handle_condition_create(message)
        elif message.type == MessageType.ConditionDelete:
            return hub_handle_condition_delete(message)
        elif message.type == MessageType.GetDevice:
            return hub_handle_get_device(message)
        else:
            logger.error(f"{message.hub_id} -- Invalid Message: Unknown type in message")
    except (InvalidDevice, InvalidLeaf, PermissionDenied, InvalidMessage) as e:
        logger.error(f"{message.hub_id} -- {e} in handling {message.type} for {message.data['uuid']}")
        reply = e.get_error_message()
        reply['hub'] = message.hub.id
        message.reply(reply)


@channel_session_user_from_http
def ws_add(message, id):
    # Accept the connection
    if Hub.objects.filter(id=id).exists():
        message.channel_session['hub'] = id
    message.reply_channel.send({"accept": True})


@channel_session_user_from_http
def ws_disconnect(message):
    if 'user' in message.channel_session:
        hub = Hub.objects.get(pk=message.channel_session['hub'])
        leaf = hub.get_leaf(message.channel_session['uuid'])
        leaf.is_connected = leaf.last_connected.timestamp() != message.channel_session['connect_time']
        leaf.save()
        MessageV1.unregister_leaf(message, leaf)


@channel_session_user
def ws_message(message):
    try:
        handle(MessageV1(message))
    except InvalidMessage:
        logger.error("Failed to handle message, aborting.")


def hub_handle_config(message: Message):
    uuid = message.data['uuid']
    username = f"{message.hub.id}-{uuid}"

    user = authenticate(username=username, password=message.data['token'])
    if user:
        try:
            leaf = message.hub.get_leaf(uuid)
            leaf.api_version = message.data['api_version']
            leaf.name = message.data['name']
            leaf.model = message.data['model']
        except InvalidLeaf:
            leaf = Leaf.create_from_message(message.data, message.hub)
            leaf.hub = message.hub
        leaf.last_connected = timezone.now()
        leaf.is_connected = True
        leaf.save()
        message.save_session_info('connect_time', leaf.last_connected.timestamp())
        message.register_leaf(leaf)
        message.save_session_info('user', user.username)
        message.save_session_info('uuid', uuid)
        response = {"type": "CONFIG_COMPLETE", "hub": message.hub.id, "uuid": uuid}
        message.reply(response)
        leaf.refresh_devices()
        logger.info(f'{message.hub.id} -- Config received for {leaf.name}')
    else:
        logger.error(f"{message.hub.id} -- Authentication failed for {uuid}")
        response = {"type": "CONFIG_FAILED", "hub": message.hub.id, "uuid": uuid}
        message.reply(response)


def hub_handle_status(message):
    hub = message.hub
    leaf = message.leaf
    device_name = message.data["device"]

    try:
        device = leaf.get_device(device_name, False)
    except Device.DoesNotExist:
        device = Device.create_from_message(message.data, hub)
        device.save()
        device.leaf.update_time()

    device.value = message.data['value']
    logger.info(f'{hub.id} -- Status updated: {device}')


def hub_handle_subscribe(message):
    target_uuid = message.data['sub_uuid'].lower()
    subscriber_uuid = message.leaf.uuid.lower()
    device = message.data['sub_device'].lower()

    if device == 'leaf':
        message.hub.get_leaf(target_uuid)
    else:
        message.hub.get_device(target_uuid, device)

    try:
        message.hub.subscriptions.get(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid, target_device=device)
        logger.info(f"{message.hub.id} -- <{subscriber_uuid}> subscribed to <{target_uuid}-{device}>")
    except ObjectDoesNotExist:
        subscription = Subscription(subscriber_uuid=subscriber_uuid, target_uuid=target_uuid,
                                    target_device=device, hub=message.hub)
        subscription.save()


def hub_handle_unsubscribe(message):
    target_uuid = message.data['sub_uuid'].lower()
    subscriber_uuid = message.leaf.uuid.lower()
    device = message.data['sub_device'].lower()

    if device == 'leaf':
        message.hub.get_leaf(target_uuid)
    else:
        message.hub.get_device(target_uuid, device)

    try:
        subscription = message.hub.subscriptions.get(subscriber_uuid=subscriber_uuid,
                                                     target_uuid=target_uuid, target_device=device)
        subscription.delete()
        logger.info(f"{message.hub.id} -- <{subscriber_uuid}> unsubscribed from <{target_uuid}-{device}>")
    except ObjectDoesNotExist:
        return


def hub_handle_get_device(message):
    pass


def hub_handle_datastore_create(message):
    uuid = message.leaf.uuid.lower()

    def give_permissions(user, level):
        if user != 'default':
            try:
                user = get_user(user, message.hub.id)
            except User.DoesNotExist:
                return
        else:
            user = PermGroup.objects.get(name='default')

        if level == 'read':
            assign_perm('view_datastore', user, datastore)
            remove_perm('change_datastore', user, datastore)
            remove_perm('delete_datastore', user, datastore)
        elif level == 'write':
            assign_perm('view_datastore', user, datastore)
            assign_perm('change_datastore', user, datastore)
            remove_perm('delete_datastore', user, datastore)
        elif level == 'admin':
            assign_perm('view_datastore', user, datastore)
            assign_perm('change_datastore', user, datastore)
            assign_perm('delete_datastore', user, datastore)
        elif level == 'deny':
            remove_perm('view_datastore', user, datastore)
            remove_perm('change_datastore', user, datastore)
            remove_perm('delete_datastore', user, datastore)

    if not message.hub.datastores.filter(name=message.data['name']).exists():
        units = message.data['units'] if 'units' in message.data else None
        value = create_value(message.data['format'], message.data['value'], units)
        value.save()
        datastore = Datastore(name=message.data['name'], _value=value, hub=message.hub)
        datastore.save()

        if 'permissions' in message.data:  # apply permissions if provided
            for leaf in message.data['permissions']:
                give_permissions(leaf, message.data['permissions'][leaf])
        else:
            give_permissions('default', 'read')  # give default read otherwise

        give_permissions(uuid, 'admin')
        reply = {
            'type': 'DATASTORE_CREATED',
            'hub': message.hub.id,
            'name': datastore.name,
            'format': datastore.format
        }
        message.reply(reply)
        logger.info(f"{message.hub.id} -- Datastore created: {message.data['name']}")


def hub_handle_datastore_get(message):
    try:
        datastore = message.hub.datastores.get(name=message.data['name'])
        user = User.objects.get(username=message.leaf.username)
        if user.has_perm('view_datastore', datastore):
            reply = {
                'type': 'DATASTORE_VALUE',
                'hub': message.hub.id,
                'name': datastore.name,
                'value': datastore.value,
                'format': datastore.format
            }
            message.reply(reply)
        else:
            raise PermissionDenied(message.leaf.uuid, 'DATASTORE_GET', name=message.data['name'])
    except Datastore.DoesNotExist:
        reply = {
            'type': 'UNKNOWN_DATASTORE',
            'hub': message.hub.id,
            'request': 'DATASTORE_GET',
            'name': message.data['name']
        }
        message.reply(reply)


def hub_handle_datastore_set(message):
    try:
        datastore = message.hub.datastores.get(name=message.data['name'])
        user = User.objects.get(username=message.leaf.username)
        if user.has_perm('change_datastore', datastore):
            datastore.value = message.data['value']
            reply = {
                'type': 'DATASTORE_VALUE',
                'hub': message.hub.id,
                'name': datastore.name,
                'value': datastore.value,
                'format': datastore.format
            }
            message.reply(reply)
            logger.info(f"{message.hub.id} -- Datastore updated: {datastore}")
        else:
            raise PermissionDenied(message.leaf.uuid, 'DATASTORE_SET', name=message.data['name'])
    except Datastore.DoesNotExist:
        reply = {
            'type': 'UNKNOWN_DATASTORE',
            'hub': message.hub.id,
            'request': 'DATASTORE_SET',
            'name': message.data['name']
        }
        message.reply(reply)


def hub_handle_datastore_delete(message):
    try:
        datastore = message.hub.datastores.get(name=message.data['name'])
        user = User.objects.get(username=message.leaf.username)
        if user.has_perm('delete_datastore', datastore):
            datastore.delete()
            reply = {'type': 'DATASTORE_DELETED',
                     'hub': message.hub.id,
                     'name': message.data['name']}
            message.reply_channel.send({'text': json.dumps(reply)})
        else:
            raise PermissionDenied(message.leaf.uuid, 'DATASTORE_DELETE', name=message.data['name'])
    except Datastore.DoesNotExist:
        reply = {
            'type': 'UNKNOWN_DATASTORE',
            'hub': message.hub.id,
            'request': 'DATASTORE_DELETE',
            'name': message.data['name']
        }
        message.reply(reply)


def hub_handle_condition_create(message):
    create_condition(message.data['name'], message.data['predicate'], message.data['actions'], message.hub)


def create_condition(name, pred, actions, hub):
    operators = {'AND': AND, 'OR': OR, 'XOR': XOR}
    seen_devices = set()

    def eval_predicates(predicates):
        first = predicates[0]
        if first == 'NOT':
            predicate = eval_predicates(predicates[1])
            not_predicate = NOT(predicate)
            not_predicate.save()
            return not_predicate
        elif type(first) == str and first in operators:
            operator_predicate = operators[first].objects.create()
            predicates = [eval_predicates(operand) for operand in predicates[1]]
            for predicate in predicates:
                predicate.operator = operator_predicate
                predicate.save()
            return operator_predicate
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
                raise InvalidPredicate(pred, name)

            predicate.save()
            return predicate

    predicate = eval_predicates(pred)

    # save condition, deleting old one if exists
    condition = Condition(name=name, predicate=predicate, hub=hub)
    try:
        old_condition = hub.conditions.get(name=name)
        old_condition.delete()
    except ObjectDoesNotExist:
        pass
    condition.save()

    # create action
    for action in actions:
        target_uuid, target_device = action['target'], action['device']
        output_device = hub.get_device(target_uuid, target_device)
        output_format = output_device.format
        if isinstance(output_device, Datastore) or output_device.mode == 'OUT':
            value = create_value(output_format, action['value'])
            value.save()

            if type(action['value']) != list:
                value = create_value(output_format, value=action['value'])
                value.save()
            else:
                remote_uuid, remote_device = action['value']
                seen_devices.add((remote_uuid, remote_device))
                value = hub.get_device(remote_uuid, remote_device)._value

            if action['action_type'] == 'SET':
                action = SetAction(target_uuid=target_uuid, target_device=target_device,
                                   _value=value, condition=condition)
                action.save()
            elif action['action_type'] == 'CHANGE':
                action = ChangeAction(target_uuid=target_uuid, target_device=target_device,
                                      _value=value, condition=condition)
                action.save()
        else:
            raise InvalidDevice(hub.get_leaf(target_uuid), output_device, InvalidDevice.MODE)

    for target, device in seen_devices:
        cond_sub = ConditionalSubscription(target_uuid=target, target_device=device, condition=condition, hub=hub)
        cond_sub.save()
    logger.info(f"{hub.id} -- {condition.name} condition set up")


def hub_handle_condition_delete(message):
    try:
        condition = message.hub.conditions.get(name=message.data['name'])
        condition.delete()
    except ObjectDoesNotExist:
        logger.error(f"{message.hub.id} -- tried to delete {message.data['name']} condition that does not exist")
