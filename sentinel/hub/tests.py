from django.test import TestCase
from channels import Channel
from channels.test import ChannelTestCase
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
        self.channel = Channel(url)

    def send(self, content):
        self.channel.send(json.loads(content))

    def connect(self, url):
        self.channel = Channel(url)
        self.on_open(self)

    def recieve_message(self, message):
        self.on_message(json.dumps(message))

    def run_forever(self):
        self.on_open(self)

    def close(self):
        self.keep_running = False


class LeafTests(ChannelTestCase):

    def setUp(self):
        def create_socket(socket, on_open, on_close, on_message, on_error):
            return FakeSocket(socket, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
        PyLeaf.create_socket = create_socket

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
        leaf = Leaf.create_from_message(fake_message) #attempt create
        self.assertEqual(leaf.name, 'python_leaf_test', "Leaf name incorrect")
        self.assertEqual(leaf.model, '01', "Leaf name incorrect")
        self.assertEqual(leaf.uuid, 'a581b491-da64-4895-9bb6-5f8d76ebd44e', "Leaf name incorrect")
        self.assertEqual(leaf.api_version, PyLeaf.API_VERSION, "Leaf name incorrect")
        #set up devices
        fake_message = {'type': 'DEVICE_LIST',
                        'uuid': leaf.uuid,
                        'devices': [{'name': 'rfid', 'value': 0,
                                    'format': 'number', 'mode': 'IN'},
                                    {'name': 'door', 'value': False,
                                    'format': 'bool', 'mode': 'OUT'}]}
        Device.create_from_device_list(fake_message)
        for device in leaf.devices.all():
            if device.name == 'rfid':
                assert
            elif device.name == 'door':
                pass
            else:
                self.fail("Unexpected device")
        d2 = PyDevice("door", True, "bool")

    def test_update_device(self):
        pass

    def test_device_types(self):
        pass

class HubTests(TestCase):
    pass

class LeafClientTest(TestCase):
    pass