from django.test import TestCase
from channels import Channel, route
from .consumers import ws_add, ws_handle_subscribe, ws_message, ws_disconnect, ws_handle_config, ws_handle_status
from channels.test import ChannelTestCase, WSClient, HttpClient, apply_routes
from django.core.exceptions import ObjectDoesNotExist
from channels import Group
from .models import Leaf, Device, BooleanDevice, StringDevice, NumberDevice, UnitDevice
from PyLeaf import PyLeaf
from PyLeaf import Device as PyDevice
import json


class FakeSocket:
    def __init__(self, url, on_open=None, on_close=None, on_message=None, on_error=None):
        self.on_message = on_message
        self.on_close = on_close
        self.keep_running = True
        self.on_open = on_open
        self.on_error = on_error
        self.client = WSClient()

    def send(self, content):
        self.client.send_and_consume('websocket.receive', json.loads(content))

    def connect(self, url):
        self.client = WSClient()
        self.client.send_and_consume('websocket.connect', {})
        self.on_open(self)

    def receive_message(self, message):
        self.on_message(json.dumps(message))

    def run_forever(self):
        self.on_open(self)

    def close(self):
        self.keep_running = False

class LeafTests(ChannelTestCase):

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
        for device in leaf.devices:
            if device.name != 'rfid' and device.name != 'door':
                self.fail("Unexpected device")
            num_found += 1
        self.assertEqual(num_found, 2, "Expected to find 2 devices")
        d2 = PyDevice("door", True, "bool")


class HubTests(TestCase):
    pass


@apply_routes([route('websocket.connect', lambda request: ws_add(request, "hub")),
               route('websocket.receive', ws_message)])
class ConsumerTests(TestCase):

    def setUp(self):
        def create_socket(socket, on_open, on_close, on_message, on_error):
            return FakeSocket(socket, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
        PyLeaf.create_socket = create_socket

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
    def send_device_update(client, leaf, device, value, format, mode="IN", options=None, units=None):
        device_message = {'type': 'DEVICE_STATUS',
                          'uuid': leaf.uuid,
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
        self.send_device_update(client, db_leaf, 'rfid_reader', 125, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf, 'door', False, 'bool', "OUT")
        self.send_device_update(client, db_leaf, 'thermometer', 50, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf, 'led_display', "BLUE LIGHT MODE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        db_leaf.refresh_from_db() # refresh leaf
        devices = {device.name: device for device in db_leaf.devices}
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
        self.send_device_update(client, db_leaf, 'rfid_reader', 33790, 'number', "IN", {'auto': 1})
        self.send_device_update(client, db_leaf, 'thermometer', 90, 'number+units', "IN", {'auto': 1}, units="F")
        self.send_device_update(client, db_leaf, 'led_display', "HERE WE", 'string', "OUT", {'auto': 1})
        self.assertIsNone(client.receive(), "Didn't  expect a response")

        db_leaf.refresh_from_db()
        devices = {device.name: device for device in db_leaf.devices}
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
    def send_subscribe(observer_client, observer_leaf, other_leaf, other_device):
        sub_message = {'type': 'SUBSCRIBE',
                       'uuid': observer_leaf.uuid,
                       'sub_uuid': other_leaf.uuid,
                       'sub_device': other_device}
        observer_client.send_and_consume('websocket.receive', {'text': sub_message})

    def test_subscriptions(self):
        # setup leaves
        rfid_client, rfid_leaf = self.send_create_leaf('rfid_leaf', '0', 'a581b491-da64-4895-9bb6-5f8d76ebd44e')
        observer_client, observer_leaf = self.send_create_leaf('rfid_leaf', '0', 'cd1b7879-d17a-47e5-bc14-26b3fc554e49')

        # setup devices
        self.send_device_update(rfid_client, rfid_leaf, 'rfid_reader', 33790, 'number')
        self.send_device_update(rfid_client, rfid_leaf, 'other_sensor', False, 'bool')

        self.send_subscribe(observer_client, observer_leaf, rfid_leaf, 'rfid_reader')  # subscribe to the rfid reader

        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # update rfid device
        self.send_device_update(rfid_client, rfid_leaf, 'rfid_reader', 3032042781, 'number')
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
        self.send_device_update(rfid_client, rfid_leaf, 'other_sensor', False, 'bool')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test full-leaf subscription
        self.send_subscribe(observer_client, observer_leaf, rfid_leaf, 'leaf')
        self.assertIsNone(observer_client.receive(), "Didn't  expect a response")
        self.assertIsNone(rfid_client.receive(), "Didn't  expect a response")

        # test that other device now generates subscription event
        self.send_device_update(rfid_client, rfid_leaf, 'other_sensor', True, 'bool')
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

        # ensure original device still generates event
        self.send_device_update(rfid_client, rfid_leaf, 'rfid_reader', 33790, 'number')
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
        pass


