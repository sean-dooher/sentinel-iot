import unittest
from .routing import websocket_routing
from channels.test import ChannelTestCase, WSClient, apply_routes
from django.core.exceptions import ObjectDoesNotExist
from channels import Group
from .models import Leaf, Hub
import logging

logging.disable(logging.ERROR)


@apply_routes(websocket_routing)
class ConsumerTests(ChannelTestCase):
    def create_hub(self, name, id="0e5ef7ab-b6b8-4563-8a47-816f0eb72be4"):
        hub = Hub(name=name, id=id)
        hub.save()
        return hub

    def send_create_leaf(self, name, model, uuid, hub, api_version="0.1.0", receive=True):
        client = WSClient()
        client.send_and_consume('websocket.connect', path=hub.id)
        config_message = {'type': 'CONFIG',
                          'name': name,
                          'model': model,
                          'uuid': uuid,
                          'password': "tests",
                          'api_version': api_version}
        client.send_and_consume('websocket.receive', {'text': config_message})
        if receive:
            self.assertIsNotNone(client.receive(), "CONFIG_COMPLETE not received")
            self.assertIsNotNone(client.receive(), "LIST_DEVICES not received")

        try:
            db_leaf = Leaf.objects.get(uuid=uuid, hub=hub)
        except ObjectDoesNotExist:
            self.fail("Failed to find leaf in db after creation")

        return client, db_leaf

    @staticmethod
    def send_device_update(client, sender, device, value, format, mode="IN", options=None, units=None):
        device_message = {'type': 'DEVICE_STATUS',
                          'uuid': sender,
                          'device': device,
                          'mode': mode,
                          'format': format,
                          'value': value}
        if options:
            device_message['options'] = options
        if units:
            device_message['units'] = units
        client.send_and_consume('websocket.receive', {'text': device_message})


    @staticmethod
    def send_subscribe(observer_client, observer_uuid, other_uuid, other_device):
        sub_message = {'type': 'SUBSCRIBE',
                       'uuid': observer_uuid,
                       'sub_uuid': other_uuid,
                       'sub_device': other_device}
        observer_client.send_and_consume('websocket.receive', {'text': sub_message})

    @staticmethod
    def send_unsubscribe(observer_client, observer_uuid, other_uuid, other_device):
        sub_message = {'type': 'UNSUBSCRIBE',
                       'uuid': observer_uuid,
                       'sub_uuid': other_uuid,
                       'sub_device': other_device}
        observer_client.send_and_consume('websocket.receive', {'text': sub_message})

    def assertDatastoreReadSuccess(self, client, requester, name, expected_value=None, expected_format=None):
        self.send_get_datastore(client, requester, name)
        expected_response = {
            'type': 'DATASTORE_VALUE',
            'name': name,
            'value': expected_value,  # value should not have changed from last set request
            'format': expected_format
        }
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response after requesting data")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['name'], expected_response['name'])
        self.assertEquals(response['value'], expected_response['value'])
        self.assertEquals(response['format'], expected_response['format'])

    def assertDatastoreReadFailed(self, client, requester, name):
        expected_response = {
                                'type': 'PERMISSION_DENIED',
                                'request': 'DATASTORE_GET',
                                'name': name,
        }
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['request'], expected_response['request'])
        self.assertEquals(response['name'], expected_response['name'])

    def assertDatastoreSetFailed(self, client, requester, name, value):
        self.send_set_datastore(client, requester, name, value)
        expected_response = {
            'type': 'PERMISSION_DENIED',
            'request': 'DATASTORE_SET',
            'name': name,
        }
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response from setting datastore value")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['request'], expected_response['request'])
        self.assertEquals(response['name'], expected_response['name'])

    def assertDatastoreDeleteFailed(self, client, requester, name):
        self.send_delete_datastore(client, requester, name)
        expected_response = {
            'type': 'PERMISSION_DENIED',
            'request': 'DATASTORE_DELETE',
            'name': name,
        }
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response from deleting datastore value")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['request'], expected_response['request'])
        self.assertEquals(response['name'], expected_response['name'])

    def assertUnknownDatastore(self, client, requester, name, method='GET', set_value=None):
        if method == 'GET':
            self.send_get_datastore(client, requester, name)
        else:
            self.send_set_datastore(client, requester, name, set_value)
        expected_response = {
            'type': 'UNKNOWN_DATASTORE',
            'request': 'DATASTORE_' + method,
            'name': name,
        }
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['request'], expected_response['request'])
        self.assertEquals(response['name'], expected_response['name'])

    @staticmethod
    def send_create_datastore(client, requester, name, value, format, permissions={}):
        data_message = {
            'type': 'DATASTORE_CREATE',
            'uuid': requester,
            'name': name,
            'value': value,
            'format': format,
        }
        if permissions:
            data_message['permissions'] = permissions
        client.send_and_consume('websocket.receive', {'text': data_message})

    @staticmethod
    def send_delete_datastore(client, requester, name):
        data_message = {
            'type': 'DATASTORE_DELETE',
            'uuid': requester,
            'name': name,
        }
        client.send_and_consume('websocket.receive', {'text': data_message})

    @staticmethod
    def send_set_datastore(client, requester, name, value):
        data_message = {
            'type': 'DATASTORE_SET',
            'uuid': requester,
            'name': name,
            'value': value
        }
        client.send_and_consume('websocket.receive', {'text': data_message})

    @staticmethod
    def send_get_datastore(client, requester, name):
        data_message = {
            'type': 'DATASTORE_GET',
            'uuid': requester,
            'name': name
        }
        client.send_and_consume('websocket.receive', {'text': data_message})

    @staticmethod
    def send_create_condition(admin_client, admin_uuid, condition_name, predicate, action_type,
                              action_target, action_device, action_value=None):
        message = {'type': 'CONDITION_CREATE',
                   'uuid': admin_uuid,
                   'name': condition_name,
                   'predicate': predicate,
                   'action': {
                       'action_type': action_type,
                       'target': action_target,
                       'device': action_device
                    }
                   }
        if action_value is not None:
            message['action']['value'] = action_value
        admin_client.send_and_consume('websocket.receive', {'text': message})

    @staticmethod
    def send_delete_condition(admin_client, admin_uuid, condition_name):
        message = {'type': 'CONDITION_DELETE',
                   'uuid': admin_uuid,
                   'name': condition_name}
        admin_client.send_and_consume('websocket.receive', {'text': message})


class LeafTests(ConsumerTests):
    def test_create(self):
        """
        Tests creating a leaf
        """
        hub = self.create_hub("test_hub")
        name = "py_create_test"
        model = "01"
        uuid = "a581b491-da64-4895-9bb6-5f8d76ebd44e"
        api_version = "3.2.3"
        client, db_leaf = self.send_create_leaf(name, model, uuid, hub, api_version, False)

        self.assertEqual(db_leaf.name, name, "Wrong name")
        self.assertEqual(db_leaf.model, model, "Wrong model")
        self.assertEqual(db_leaf.uuid, uuid, "Wrong uuid")
        self.assertEqual(db_leaf.api_version, api_version, "Wrong api_version")

        response = client.receive()
        self.assertIsNotNone(response, "Expected a response")
        self.assertEqual(response['type'], 'CONFIG_COMPLETE')
        response = client.receive()
        self.assertIsNotNone(response, "Expected a response")
        self.assertEqual(response['type'], 'LIST_DEVICES')
        response = client.receive()
        self.assertIsNone(response, "Only expected two responses")

        # ensure that using group to talk to client works
        Group(f"{db_leaf.hub.id}-{db_leaf.uuid}").send({'text': {}})
        self.assertIsNotNone(client.receive(), "Expected a response")

    def test_devices(self):
        hub = self.create_hub("test_hub")
        name = "py_device_test"
        model = "01"
        uuid = "a581b491-da64-4895-9bb6-5f8d76ebd44e"
        client, db_leaf = self.send_create_leaf(name, model, uuid, hub)

        # send initial values, create devices in database
        self.send_device_update(client, db_leaf.uuid, 'rfid_reader', 125, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf.uuid, 'door', False, 'bool', "OUT")
        self.send_device_update(client, db_leaf.uuid, 'thermometer', 50, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf.uuid, 'led_display', "BLUE LIGHT MODE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        self.assertEqual(db_leaf.devices.count(), 4, "Expected four devices")
        devices = {device.name:device for device in db_leaf.devices.all()}
        # TODO: uncomment options
        # test all devices
        self.assertTrue('rfid_reader' in devices)  # tests name implicitly
        rfid_device = devices['rfid_reader']
        self.assertEquals(rfid_device.format, 'number', "Expected rfid to be a number device")
        self.assertEquals(rfid_device.value, 125, "Wrong value")
        # self.assertDictEqual({'auto': 1}, rfid_device.options, "Wrong options dictionary")

        self.assertTrue('door' in devices)
        door_device = devices['door']
        self.assertEquals(door_device.format, 'bool', "Expected door to be a boolean device")
        self.assertEquals(door_device.value, 0, "Wrong value")
        # self.assertDictEqual({}, door_device.options, "Wrong options dictionary")

        self.assertTrue('thermometer' in devices)
        thermometer_device = devices['thermometer']
        self.assertEquals(thermometer_device.format, 'number+units', "Expected device to be a number+unit device")
        self.assertEquals(thermometer_device.value, 50, "Wrong value")
        # self.assertDictEqual({'auto': 1}, thermometer_devide.options, "Wrong options dictionary")

        self.assertTrue('led_display' in devices)
        led_device = devices['led_display']
        self.assertEquals(led_device.format, 'string', "Expected device to be a number+unit device")
        self.assertEquals(led_device.value, "BLUE LIGHT MODE", "Wrong value")
        # self.assertDictEqual({'auto': 1}, led_device.options, "Wrong options dictionary")

        # test updating by updating all but door
        self.send_device_update(client, db_leaf.uuid, 'rfid_reader', 33790, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf.uuid, 'thermometer', 90, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf.uuid, 'led_display', "HERE WE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        self.assertEqual(db_leaf.devices.count(), 4, "Expected four devices")

        # refresh all devices to check for changes
        rfid_device.refresh_from_db()
        door_device.refresh_from_db()
        led_device.refresh_from_db()
        thermometer_device.refresh_from_db()

        self.assertEquals(rfid_device.value, 33790, "Wrong value")
        self.assertEquals(door_device.value, False, "Wrong value")  # make sure door didn't change
        self.assertEquals(led_device.value, "HERE WE", "Wrong value")
        self.assertEquals(thermometer_device.value, 90, "Wrong value")

    @unittest.skip("Options not implemented yet")
    def test_options(self):
        pass

    def test_subscriptions(self):
        hub = self.create_hub("test_hub")

        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        # setup devices
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')

        # subscribe
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'rfid_reader')

        # update rfid device
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test that subscription message was received and check parameters
        sub_message = observer_client.receive()
        self.assertIsNotNone(sub_message, "Expected to receive a subscription update")
        self.assertEquals(sub_message['type'], 'SUBSCRIPTION_UPDATE', "Wrong type")
        self.assertEquals(sub_message['sub_uuid'], rfid_leaf.uuid, "Wrong uuid")
        self.assertEquals(sub_message['sub_device'], 'rfid_reader', "Wrong device")
        sub_status = {'type': 'DEVICE_STATUS',
                      'device': 'rfid_reader',
                      'format': 'number',
                      'value': 3032042781}

        for key in sub_status: # check that the message has the right values
            self.assertEquals(sub_message['message'][key], sub_status[key])

        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")  # make sure there are no more messages

        # make sure other device doesn't trigger subscription event
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

    def test_full_leaf_subscribe(self):
        hub = self.create_hub("test_hub")

        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        # setup devices
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')

        # subscribe to the rfid reader
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'rfid_reader')
        # subscribe to whole leaf
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'leaf')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test that other device generates subscription event
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', True, 'bool')
        sub_message = observer_client.receive()
        self.assertIsNotNone(sub_message, "Expected to receive a subscription update")
        self.assertEquals(sub_message['type'], 'SUBSCRIPTION_UPDATE', "Wrong type")
        self.assertEquals(sub_message['sub_uuid'], rfid_leaf.uuid, "Wrong uuid")
        self.assertEquals(sub_message['sub_device'], 'leaf', "Wrong device")
        sub_status = {'type': 'DEVICE_STATUS',
                      'device': 'other_sensor',
                      'format': 'bool',
                      'value': True}

        for key in sub_status:
            self.assertEquals(sub_message['message'][key], sub_status[key])

        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")  # ensure there are no more messages

        # ensure original device generates event
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        sub_message = observer_client.receive()
        self.assertIsNotNone(sub_message, "Expected to receive a subscription update")
        self.assertEquals(sub_message['type'], 'SUBSCRIPTION_UPDATE', "Wrong type")
        self.assertEquals(sub_message['sub_uuid'], rfid_leaf.uuid, "Wrong uuid")
        self.assertEquals(sub_message['sub_device'], 'rfid_reader', "Wrong device")
        # ensure message doesn't show up twice
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")

    def test_unsubscribe(self):
        hub = self.create_hub("test_hub")

        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        # setup devices
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')

        # subscribe to rfid_leaf
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'rfid_reader')

        # update rfid device
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test that subscription message was received
        self.assertIsNotNone(observer_client.receive(), "Expected to receive a subscription update")

        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")  # make sure there are no more messages

        # unsubscribe
        self.send_unsubscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'rfid_reader')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')

        self.assertIsNone(observer_client.receive())  # should not receive subscription updates any more

    def test_full_leaf_unsubscribe(self):
        hub = self.create_hub("test_hub")

        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        # setup devices
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')

        # subscribe to the rfid reader
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'rfid_reader')
        # subscribe to whole leaf
        self.send_subscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'leaf')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test that other device generates subscription event
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', True, 'bool')
        self.assertIsNotNone(observer_client.receive(), "Expected to receive a subscription update")
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")  # ensure there are no more messages

        # ensure original device generates event
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.assertIsNotNone(observer_client.receive(), "Expected to receive a subscription update")
        # ensure message doesn't show up twice
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")

        # unsubscribe and make sure other sensor doesn't generate subscription events anymore
        self.send_unsubscribe(observer_client, observer_leaf.uuid, rfid_leaf.uuid, 'leaf')
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'other_sensor', False, 'bool')
        self.assertIsNone(observer_client.receive(), "Did not expect a message from other_sensor after unsubscribing")

        # make sure that the original subscription to the rfid_reader still exists
        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.assertIsNotNone(observer_client.receive(), "Expected to still receive a subscription update")


@unittest.skip("Datastores not implemented yet")
class DatastoreTests(ConsumerTests):
    def test_datastore_create_delete(self):
        hub = self.create_hub("test_hub")
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)

        # make sure the datastore didn't exist beforehand
        self.assertUnknownDatastore(rfid_client, rfid_leaf.uuid, 'sean_home', 'GET')
        self.assertUnknownDatastore(rfid_client, rfid_leaf.uuid, 'sean_home', 'SET', False)

        # test create
        self.send_create_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')
        expected_response = {
            'type': 'DATASTORE_CREATED',
            'name': 'sean_home',
            'format': 'bool',
        }
        response = rfid_client.receive()
        self.assertIsNotNone(response, "Expected a message for creating datastore")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['name'], expected_response['name'])
        self.assertEquals(response['format'], expected_response['format'])

        # make sure value was saved
        self.assertDatastoreReadSuccess(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')

        # test delete
        self.send_delete_datastore(rfid_client, rfid_leaf.uuid, 'sean_home')
        expected_response = {
            'type': 'DATASTORE_DELETED',
            'name': 'sean_home'
        }
        response = rfid_client.receive()
        self.assertIsNotNone(response, "Expected a message for creating datastore")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['name'], expected_response['name'])

        # make sure delete was successful
        self.assertUnknownDatastore(rfid_client, rfid_leaf.uuid, 'sean_home', 'GET')
        self.assertUnknownDatastore(rfid_client, rfid_leaf.uuid, 'sean_home', 'SET', False)

    def test_datastore_update(self):
        hub = self.create_hub("test_hub")
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        self.send_create_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')
        self.assertIsNotNone(rfid_client.receive(), "Expected creation message")
        # set new value and check for success with a read

        self.assertDatastoreReadSuccess(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')
        self.send_set_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', True)
        self.assertDatastoreReadSuccess(rfid_client, rfid_leaf.uuid, 'sean_home', True, 'bool')

    def test_datastore_permissions(self):
        hub = self.create_hub("test_hub")
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)
        light_client, light_leaf = self.send_create_leaf('light_leaf', '0', '3cbb357f-3dda-4463-9055-581b82ab8690', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)

        permissions = {
            'default': 'deny',  # deny reads and writes by default
            'cd1b7879-d17a-47e5-bc14-26b3fc554e49': 'read',  # the door can read the value
            '3cbb357f-3dda-4463-9055-581b82ab8690': 'write',  # the other_client can read and write
            '2e11b9fc-5725-4843-8b9c-4caf2d69c499': 'admin'
        }
        self.send_create_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool', permissions)
        self.assertIsNotNone(rfid_client.receive(), "Expected a response from creating datastore")

        # test deny
        self.assertDatastoreReadFailed(other_client, other_leaf.uuid, 'sean_home')
        self.assertDatastoreSetFailed(other_client, other_leaf.uuid, 'sean_home', True)
        self.assertDatastoreDeleteFailed(other_client, other_leaf.uuid, 'sean_home')

        # test read
        self.assertDatastoreReadSuccess(door_client, door_leaf.uuid, 'sean_home', False, 'bool')
        self.assertDatastoreSetFailed(door_client, door_leaf.uuid, 'sean_home', True)
        self.assertDatastoreDeleteFailed(door_client, door_leaf.uuid, 'sean_home')

        # test write
        # ensures write read works and last 'set' was not successful
        self.assertDatastoreReadSuccess(light_client, light_leaf.uuid, 'sean_home', True, 'bool')

        self.send_set_datastore(light_client, light_leaf.uuid, 'sean_home', True)
        self.assertIsNone(light_client.receive(), "Did not expect a message after updating")

        self.assertDatastoreReadSuccess(light_client, light_leaf.uuid, 'sean_home', True, 'bool')
        self.assertDatastoreDeleteFailed(light_client, light_leaf.uuid, 'sean_home')
        # test admin
        self.send_set_datastore(admin_client, admin_leaf.uuid, 'sean_home', False)
        self.assertIsNone(admin_client.receive(), "Did not expect a message after updating")

        self.assertDatastoreReadSuccess(admin_client, admin_leaf.uuid, 'sean_home', False, 'bool')
        self.send_delete_datastore(admin_client, admin_leaf.uuid, 'sean_home')
        expected_response = {
            'type': 'DATASTORE_DELETED',
            'name': 'sean_home'
        }
        response = admin_client.receive()
        self.assertIsNotNone(response, "Expected a message for creating datastore")
        self.assertEquals(response['type'], expected_response['type'])
        self.assertEquals(response['name'], expected_response['name'])


class ConditionsTests(ConsumerTests):
    def test_basic_conditions(self):
        hub = self.create_hub("test_hub")

        def test_basic(operator, literal, initial, wrong, right):
            name = 'basic_' + operator + str(literal)
            admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
            rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
            door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

            self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', initial, 'number')
            self.send_device_update(door_client, door_leaf.uuid, 'door_open', False, 'bool', mode='OUT')

            predicates = [operator, [rfid_leaf.uuid, 'rfid_reader'], literal]
            self.send_create_condition(admin_client, admin_leaf.uuid, name,
                                       predicates, action_type='SET', action_target=door_leaf.uuid,
                                       action_device='door_open', action_value=True)

            self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', wrong, 'number')
            self.assertIsNone(door_client.receive())  # condition has not been met yet
            self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', right, 'number')

            expected = {
                'type': 'SET_OUTPUT',
                'uuid': door_leaf.uuid,
                'device': 'door_open',
                'value': True,
                'format': 'bool'
            }
            response = door_client.receive()
            self.assertIsNotNone(response, "Expected a SET_OUTPUT response from condition")
            self.assertEqual(expected['type'], response['type'])
            self.assertEqual(expected['uuid'], response['uuid'])
            self.assertEqual(expected['device'], response['device'])
            self.assertEqual(expected['value'], response['value'])
            self.assertEqual(expected['format'], response['format'])
            self.assertIsNone(door_client.receive())  # only gets one update
            self.send_delete_condition(admin_client, admin_leaf.uuid, name)

        test_basic('=', 3032042781, 33790, 3032042780, 3032042781)
        test_basic('!=', 3032042781, 3032042781, 3032042781, 33790)
        test_basic('>', 0, -12, -5, 13)
        test_basic('<', 0, 12, 5, -13)
        test_basic('>=', 0, -12, -5, 0)
        test_basic('<=', 0, 12, 5, 0)

    def test_binary_and(self):
        hub = self.create_hub("test_hub")
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', False, 'bool')
        self.send_device_update(door_client, door_leaf.uuid, 'door_open', False, 'bool', mode='OUT')

        predicates = ['AND', ['=', [rfid_leaf.uuid, 'rfid_reader'], 3032042781],
                      ['=', [other_leaf.uuid, 'other_sensor'], True]]
        self.send_create_condition(admin_client, admin_leaf.uuid, 'binary_AND', predicates, action_type='SET',
                                   action_target=door_leaf.uuid, action_device='door_open', action_value=True)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(door_client.receive())  # other_sensor is false so the condition doesn't trigger

        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', True, 'bool')

        response = door_client.receive()
        self.assertIsNotNone(response, "Expected a SET_OUTPUT response from condition")
        self.assertEqual(response['type'], 'SET_OUTPUT')
        self.assertIsNone(door_client.receive())  # only gets one update
        self.send_delete_condition(admin_client, admin_leaf.uuid, "binary_AND")

    def test_binary_or(self):
        hub = self.create_hub("test_hub")
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', False, 'bool')
        self.send_device_update(door_client, door_leaf.uuid, 'door_open', False, 'bool', mode='OUT')

        predicates = ['OR', ['=', [rfid_leaf.uuid, 'rfid_reader'], 3032042781],
                      ['=', [other_leaf.uuid, 'other_sensor'], True]]
        self.send_create_condition(admin_client, admin_leaf.uuid, 'binary_OR', predicates, action_type='SET',
                                   action_target=door_leaf.uuid, action_device='door_open', action_value=True)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNotNone(door_client.receive(), "Expected a response as one condition is true")

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042780, 'number')
        self.assertIsNone(door_client.receive(), "Expected no response as both conditions are false")

        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', True, 'bool')
        self.assertIsNotNone(door_client.receive(), "Expected SET_OUTPUT as other condition is true")

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')

        self.assertIsNone(door_client.receive())  # only gets one update
        self.send_delete_condition(admin_client, admin_leaf.uuid, "binary_OR")

    def test_binary_xor(self):
        hub = self.create_hub("test_hub")
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', True, 'bool')
        self.send_device_update(door_client, door_leaf.uuid, 'door_open', False, 'bool', mode='OUT')

        predicates = ['XOR', ['=', [rfid_leaf.uuid, 'rfid_reader'], 3032042781],
                      ['=', [other_leaf.uuid, 'other_sensor'], True]]
        self.send_create_condition(admin_client, admin_leaf.uuid, 'binary_OR', predicates, action_type='SET',
                                   action_target=door_leaf.uuid, action_device='door_open', action_value=True)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(door_client.receive(), "Expected no response as both conditions are true")

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 12312, 'number')
        self.assertIsNotNone(door_client.receive(), "Expected a response as one condition is true")

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(door_client.receive(), "Expected no response as both conditions are true")

        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', False, 'bool')
        self.assertIsNotNone(door_client.receive(), "Expected a response as one condition is true")

        self.assertIsNone(door_client.receive())  # only gets one update
        self.send_delete_condition(admin_client, admin_leaf.uuid, "binary_OR")

    def test_nested(self):
        hub = self.create_hub("test_hub")
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)
        third_client, third_leaf = self.send_create_leaf('third_leaf', '0', '0e86b123-42db-46a5-a816-4c194f6d33b5', hub)
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', False, 'bool')
        self.send_device_update(third_client, third_leaf.uuid, 'third_sensor', False, 'bool')
        self.send_device_update(door_client, door_leaf.uuid, 'door_open', False, 'bool', mode='OUT')

        predicates = ['OR', ['AND', ['=', [rfid_leaf.uuid, 'rfid_reader'], 3032042781],
                             ['=', [third_leaf.uuid, 'third_sensor'], True]],
                      ['=', [other_leaf.uuid, 'other_sensor'], True]]
        self.send_create_condition(admin_client, admin_leaf.uuid, 'binary_nested', predicates, action_type='SET',
                                   action_target=door_leaf.uuid, action_device='door_open', action_value=True)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(door_client.receive(), "Expected no response as only one nested condition is true")

        self.send_device_update(third_client, third_leaf.uuid, 'third_sensor', True, 'bool')

        self.assertIsNotNone(door_client.receive(), "Expected SET_OUTPUT as both inner conditions are true")

        self.send_device_update(third_client, third_leaf.uuid, 'third_sensor', False, 'bool')
        self.assertIsNone(door_client.receive(), "Expected no response as only one nested condition is true")

        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', True, 'false')
        self.assertIsNotNone(door_client.receive(), "Expected a response as one outer condition is true")

        self.assertIsNone(door_client.receive())  # only gets one update
        self.send_delete_condition(admin_client, admin_leaf.uuid, "binary_nested")

    def test_invalid_output_device(self):
        hub = self.create_hub("test_hub")
        admin_client, admin_leaf = self.send_create_leaf('admin_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499', hub)
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub)
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub)

        self.send_device_update(rfid_client, rfid_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(other_client, other_leaf.uuid, 'other_sensor', False, 'bool')

        predicates = ['=', [rfid_leaf.uuid, 'rfid_reader'], 3032042781]
        self.send_create_condition(admin_client, admin_leaf.uuid, "invalid_output_condition",
                                   predicates, action_type='SET', action_target=other_leaf.uuid,
                                   action_device='other_sensor', action_value=True)

        response = admin_client.receive()
        self.assertIsNotNone(response, "Expected invalid device message as other_sensor is not an output")
        self.assertEquals(response['type'], 'INVALID_DEVICE')


class HubTests(ConsumerTests):
    def test_multiple_hubs_leaves(self):
        hub1 = self.create_hub("first_hub", "1")
        hub2 = self.create_hub("second_hub", "2")
        hub1_client, hub1_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub1)
        hub2_client, hub2_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub2)

        self.assertEquals(hub2.leaves.count(), 1)
        self.assertEquals(hub1.leaves.count(), 1)

        self.send_device_update(hub1_client, hub1_leaf.uuid, 'rfid', 323, 'number')
        self.assertIsNone(hub1_client.receive(), "Expected no response from both on device creation")
        self.assertIsNone(hub2_client.receive(), "Expected no response from both on device creation")

        self.assertEquals(hub2_leaf.devices.count(), 0)
        self.assertEquals(hub1_leaf.devices.count(), 1)

    def test_multiple_hubs_subscriptions(self):
        hub1 = self.create_hub("first_hub", "1")
        hub2 = self.create_hub("second_hub", "2")
        hub1_client, hub1_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub1)
        hub2_client, hub2_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub2)
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0',
                                                               'cd1b7879-d17a-47e5-bc14-26b3fc554e49', hub1)
        # set initial values
        self.send_device_update(hub1_client, hub1_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(hub2_client, hub2_leaf.uuid, 'rfid_reader', 33790, 'number')

        # subscribe
        self.send_subscribe(observer_client, observer_leaf.uuid, hub1_leaf.uuid, 'rfid_reader')

        # update rfid device
        self.send_device_update(hub1_client, hub1_leaf.uuid, 'rfid_reader', 3032042781, 'number')
        self.assertIsNone(hub1_client.receive(), "Didn't  expect a response")
        self.assertIsNone(hub2_client.receive(), "Didn't  expect a response")

        # test that subscription message was received and check parameters
        sub_message = observer_client.receive()
        self.assertIsNotNone(sub_message, "Expected to receive a subscription update")
        self.assertEquals(sub_message['type'], 'SUBSCRIPTION_UPDATE', "Expected message to be a subscription update")

        # make sure other device doesn't trigger subscription event
        self.send_device_update(hub2_client, hub2_leaf.uuid, 'rfid_reader', 3230, 'number')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(hub1_client.receive(), "Didn't  expect a response")
        self.assertIsNone(hub2_client.receive(), "Didn't  expect a response")

    def test_multiple_hubs_conditions(self):
        hub1 = self.create_hub("first_hub", "1")
        hub2 = self.create_hub("second_hub", "2")
        hub1_client, hub1_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub1)
        out_client1, out_leaf1 = self.send_create_leaf('rfid_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub1)
        hub2_client, hub2_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e', hub2)
        out_client2, out_leaf2 = self.send_create_leaf('rfid_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b', hub2)

        self.send_device_update(hub1_client, hub1_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(hub2_client, hub2_leaf.uuid, 'rfid_reader', 33790, 'number')
        self.send_device_update(out_client1, out_leaf1.uuid, 'output', False, 'bool', mode="OUT")
        self.send_device_update(out_client2, out_leaf2.uuid, 'output', False, 'bool', mode="OUT")

        predicate = ['=', [hub1_leaf.uuid, 'rfid_reader'], 3032042781]
        self.send_create_condition(hub1_client, hub1_leaf.uuid, "multi_condition",
                                   predicate, action_type='SET', action_target=out_leaf1.uuid,
                                   action_device='output', action_value=True)

        # send value that would satisfy predicate from wrong hub
        self.send_device_update(hub2_client, hub2_leaf.uuid, 'rfid_reader', 3032042781, 'number')

        # ensure no response was received by either output device
        self.assertIsNone(out_client1.receive(), "Leaf from wrong hub satisfied predicate")
        self.assertIsNone(out_client2.receive(), "Condition created on wrong hub")

        # satisfy predicate from correct hub
        self.send_device_update(hub1_client, hub1_leaf.uuid, 'rfid_reader', 3032042781, 'number')

        # ensure that only one hub receives output
        self.assertIsNotNone(out_client1.receive(), "Expected an out on hub1")
        self.assertIsNone(out_client2.receive(), "Did not expect second hub to receive output")
