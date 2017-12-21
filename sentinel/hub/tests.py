from django.test import TestCase
from channels import Channel, route
from .consumers import ws_add, ws_handle_subscribe, ws_message, ws_disconnect, ws_handle_config, ws_handle_status
from channels.test import ChannelTestCase, WSClient, HttpClient, apply_routes
from django.core.exceptions import ObjectDoesNotExist
from channels import Group
from .models import Leaf, Device, BooleanDevice, StringDevice, NumberDevice, UnitDevice
import json


class LeafModelTests(ChannelTestCase):
    def test_refresh_devices(self):
        Group("a581b491-da64-4895-9bb6-5f8d76ebd44e").add("test-channel")
        leaf = Leaf(name="test1", model="01", uuid="a581b491-da64-4895-9bb6-5f8d76ebd44e")
        d1 = BooleanDevice(name="door", leaf=leaf, value=False, is_input=False)
        leaf.refresh_device("door")
        result = self.get_next_message("test-channel", require=True)
        expected_result = {'type': 'GET_DEVICE',
                           'hub_id': 1,
                           'uuid': 'a581b491-da64-4895-9bb6-5f8d76ebd44e',
                           'device': 'door'}
        result = json.loads(result.content['text'])  # load message content as dictionary for validation
        self.assertDictEqual(expected_result, result, "Failed get device")

        leaf.refresh_devices()
        result = self.get_next_message("test-channel", require=True)
        expected_result = {'type': 'LIST_DEVICES',
                           'hub_id': 1,
                           'uuid': 'a581b491-da64-4895-9bb6-5f8d76ebd44e'}
        result = json.loads(result.content['text'])  # load message content as dictionary for validation
        self.assertDictEqual(expected_result, result, "Failed list devices")

    def test_create(self):
        # set up leaf
        fake_message = {'type': 'CONFIG',
                        'name': 'python_leaf_test',
                        'model': '01',
                        'uuid': "a581b491-da64-4895-9bb6-5f8d76ebd44e",
                        'api_version': '0.1.0'}
        leaf = Leaf.create_from_message(fake_message)  # attempt create
        leaf = Leaf.objects.get(pk=fake_message['uuid'])
        self.assertEqual(leaf.name, 'python_leaf_test', "Leaf name incorrect")
        self.assertEqual(leaf.model, '01', "Leaf model incorrect")
        self.assertEqual(leaf.uuid, 'a581b491-da64-4895-9bb6-5f8d76ebd44e', "Leaf uuid incorrect")
        self.assertEqual(leaf.api_version, '0.1.0', "Leaf api version incorrect")
        # set up devices
        fake_message = {'type': 'DEVICE_LIST',
                        'uuid': leaf.uuid,
                        'devices': [{'name': 'rfid', 'value': 0,
                                    'format': 'number', 'mode': 'IN'},
                                    {'name': 'door', 'value': False,
                                    'format': 'bool', 'mode': 'OUT'}]}
        Device.create_from_device_list(fake_message)
        num_found = 0
        for device in leaf.devices.all():
            if device.name != 'rfid' and device.name != 'door':
                self.fail("Unexpected device")
            num_found += 1
        self.assertEqual(num_found, 2, "Expected to find 2 devices")

@apply_routes([route('websocket.connect', lambda request: ws_add(request, "hub")),
               route('websocket.receive', ws_message)])
class ConsumerTests(TestCase):

    def send_create_leaf(self, name, model, uuid, api_version="0.1.0", receive=True):
        client = WSClient()
        client.send_and_consume('websocket.connect')
        config_message = {'type': 'CONFIG',
                          'name': name,
                          'model': model,
                          'uuid': uuid,
                          'api_version': api_version}
        client.send_and_consume('websocket.receive', {'text': config_message})
        if receive:
            self.assertIsNotNone(client.receive(), "LIST_DEVICES not received")
            self.assertIsNotNone(client.receive(), "CONFIG_COMPLETE not received")

        try:
            db_leaf = Leaf.objects.get(pk=uuid)
        except ObjectDoesNotExist:
            self.fail("Failed to find leaf in db after creation")

        return client, db_leaf

    def test_create(self):
        """
        Tests creating a leaf
        """
        name = "py_create_test"
        model = "01"
        uuid = "a581b491-da64-4895-9bb6-5f8d76ebd44e"
        api_version = "3.2.3"
        client, db_leaf = self.send_create_leaf(name, model, uuid, api_version, False)

        self.assertEqual(db_leaf.name, name, "Wrong name")
        self.assertEqual(db_leaf.model, model, "Wrong model")
        self.assertEqual(db_leaf.uuid, uuid, "Wrong uuid")
        self.assertEqual(db_leaf.api_version, api_version, "Wrong api_version")

        response = client.receive()
        self.assertIsNotNone(response, "Expected a response")
        self.assertEqual(response['type'], 'LIST_DEVICES')
        self.assertIsNotNone(response, "Expected a response")
        response = client.receive()
        self.assertEqual(response['type'], 'CONFIG_COMPLETE')
        response = client.receive()
        self.assertIsNone(response, "Only expected two responses")

        # ensure that using group to talk to client works
        Group(db_leaf.uuid).send({'text': {}})
        self.assertIsNotNone(client.receive(), "Expected a response")


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

    def test_devices(self):
        name = "py_device_test"
        model = "01"
        uuid = "a581b491-da64-4895-9bb6-5f8d76ebd44e"
        client, db_leaf = self.send_create_leaf(name, model, uuid)

        # send initial values, create devices in database
        self.send_device_update(client, db_leaf.uuid, 'rfid_reader', 125, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf.uuid, 'door', False, 'bool', "OUT")
        self.send_device_update(client, db_leaf.uuid, 'thermometer', 50, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf.uuid, 'led_display', "BLUE LIGHT MODE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        db_leaf.refresh_from_db() # refresh leaf
        devices = db_leaf.get_devices(False)
        self.assertEqual(len(devices), 4, "Expected four devices")

        # TODO: uncomment options
        # test all devices
        self.assertTrue('rfid_reader' in devices)  # tests name implicitly
        rfid_device = devices['rfid_reader']
        self.assertTrue(isinstance(rfid_device, NumberDevice), "Expected rfid to be a number device")
        self.assertEquals(rfid_device.value, 125, "Wrong value")
        # self.assertDictEqual({'auto': 1}, rfid_device.options, "Wrong options dictionary")

        self.assertTrue('door' in devices)
        door_device = devices['door']
        self.assertTrue(isinstance(door_device, BooleanDevice), "Expected door to be a boolean device")
        self.assertEquals(door_device.value, 0, "Wrong value")
        # self.assertDictEqual({}, door_device.options, "Wrong options dictionary")

        self.assertTrue('thermometer' in devices)
        thermometer_device = devices['thermometer']
        self.assertTrue(isinstance(thermometer_device, UnitDevice), "Expected device to be a number+unit device")
        self.assertEquals(thermometer_device.value, 50, "Wrong value")
        # self.assertDictEqual({'auto': 1}, thermometer_devide.options, "Wrong options dictionary")

        self.assertTrue('led_display' in devices)
        led_device = devices['led_display']
        self.assertTrue(isinstance(led_device, StringDevice), "Expected device to be a string device")
        self.assertEquals(led_device.value, "BLUE LIGHT MODE", "Wrong value")
        # self.assertDictEqual({'auto': 1}, led_device.options, "Wrong options dictionary")

        # test updating by updating all but door
        self.send_device_update(client, db_leaf.uuid, 'rfid_reader', 33790, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf.uuid, 'thermometer', 90, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf.uuid, 'led_display', "HERE WE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        db_leaf.refresh_from_db()
        devices = db_leaf.get_devices(False)
        self.assertEqual(len(devices), 4, "Expected four devices")

        # refresh all devices to check for changes
        rfid_device.refresh_from_db()
        door_device.refresh_from_db()
        led_device.refresh_from_db()
        thermometer_device.refresh_from_db()

        self.assertEquals(rfid_device.value, 33790, "Wrong value")
        self.assertEquals(door_device.value, False, "Wrong value")  # make sure door didn't change
        self.assertEquals(led_device.value, "HERE WE", "Wrong value")
        self.assertEquals(thermometer_device.value, 90, "Wrong value")

    def test_options(self):
        pass

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

    def test_subscriptions(self):
        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')

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
        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')

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
        sub_status = {'type': 'DEVICE_STATUS',
                      'device': 'rfid_reader',
                      'format': 'number',
                      'value': 33790}
        # ensure message doesn't show up twice
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")

    def test_unsubscribe(self):
        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')

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

        self.assertIsNone(observer_client.receive()) # should not recieve subscription updates any more

    def test_full_leaf_unsubscribe(self):
        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')

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

    def test_datastore_create_delete(self):
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')

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
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        self.send_create_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')
        self.assertIsNotNone(rfid_client.receive(), "Expected creation message")
        # set new value and check for success with a read

        self.assertDatastoreReadSuccess(rfid_client, rfid_leaf.uuid, 'sean_home', False, 'bool')
        self.send_set_datastore(rfid_client, rfid_leaf.uuid, 'sean_home', True)
        self.assertDatastoreReadSuccess(rfid_client, rfid_leaf.uuid, 'sean_home', True, 'bool')

    def test_datastore_permissions(self):
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        door_client, door_leaf = self.send_create_leaf('door_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')
        light_client, light_leaf = self.send_create_leaf('light_leaf', '0', '3cbb357f-3dda-4463-9055-581b82ab8690')
        other_client, other_leaf = self.send_create_leaf('other_leaf', '0', '7cfb0bde-7b0e-430b-a033-034eb7422f4b')
        admin_client, admin_leaf = self.send_create_leaf('other_leaf', '0', '2e11b9fc-5725-4843-8b9c-4caf2d69c499')

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

