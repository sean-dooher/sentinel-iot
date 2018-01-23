from websocket import WebSocketApp
import threading
import json


class PyLeaf:
    API_VERSION = '1.0.0'

    def __init__(self, name, model, uuid, token, socket=None):
        self.devices = {}
        self.name = name
        self.uuid = uuid
        self.model = model
        self.token = token
        self.socket = None
        self.socket_thread = None
        self.max_connect_attempt = 5
        self.connect_attempt = 0
        if socket:
            self.connect(socket)
        self.connected = False
        self.subscriptions = {}
        self.message_queue = []

    def connect(self, socket):
        assert socket, "Must connect to a url"
        self.connect_attempt += 1
        self.disconnect()

        def on_connect(ws):
            self.connect_attempt = 0
            self.connected = True
            self.send_config()

        self.socket = WebSocketApp(socket,
                                   on_open=on_connect,
                                   on_close=lambda message: self.attempt_reconnect(),
                                   on_message=lambda ws, message: self.parse_message(message),
                                   on_error=lambda ws, error: self.process_error(error))

        self.socket_thread = threading.Thread(target=self.socket.run_forever)

        # override default join behavior to shut down thread properly when exiting program
        join = self.socket_thread.join

        def thread_close():
            self.socket.keep_running = False
            self.socket.close()
            join()

        self.socket_thread.join = thread_close

        self.socket_thread.start()

    def disconnect(self):
        if self.socket:
            self.socket.on_close = None
            self.socket.on_error = None
            self.socket.keep_running = False
            self.socket.close()
            self.socket_thread.join()

    def attempt_reconnect(self):
        self.disconnect()
        if self.connect_attempt < self.max_connect_attempt:
            self.connect(self.socket.url)

    def process_error(self, error):
        print("WebSocket Error: {}".format(error))

    def send_device_list(self):
        message = {'type': 'DEVICE_LIST',
                   'uuid': self.uuid}
        for device in self.devices:
            self.send_status(device)
        self.socket.send(json.dumps(message))

    def send_name(self):
        message = {'uuid': self.uuid,
                   'type': 'NAME',
                   'name': self.name}
        self.socket.send(json.dumps(message))

    def parse_message(self, message):
        message = json.loads(message)
        if not PyLeaf.is_valid_message(message):
            message = {'type': 'INVALID_MESSAGE',
                       'uuid': self.uuid}
            self.socket.send(json.dumps(message))

        type = message["type"]
        if type == 'LIST_DEVICES':
            self.send_device_list()

        elif type == 'UPDATE_OPTION':
            device = self.get_device(message['device'])
            if device:
                if not device.set_option(message['option'], message['value']):
                    return device.send_invalid_option(message['option'])
                return device.send_option(message['option'], self.socket)
            else:
                return self.send_unknown_device(message['device'])

        elif type == 'GET_OPTION':
            device = self.get_device(message['device'])
            if device:
                return device.send_option(message['option'], self.socket)
            else:
                return self.send_unknown_device(message['device'])

        elif type == 'GET_DEVICE':
            return self.send_status(message['device'])

        elif type == 'SET_OUTPUT':
            device = self.get_device(message['device'])
            if device:
                if device.mode == Device.OUT:
                    value = device.parse_value(message['value'])
                    if value:
                        device.value = value
                        return
                    else:
                        device.send_invalid_value(message, self.socket)
                else:
                    device.send_invalid_mode(message, self.socket)
            else:
                return self.send_unknown_device()

        elif type == 'GET_CONFIG':
            return self.send_config()

        elif type == 'CONFIG_COMPLETE':
            return self.process_queue()

        elif type == 'SUBSCRIBER_UPDATE':
            sub_message = json.loads(message["message"])
            if 'uuid' in sub_message and sub_message['uuid'] in self.subscriptions:
                if 'device' in sub_message:
                    device = sub_message['device']
                else:
                    device = 'all'
                if device in self.subscriptions[sub_message['uuid']]:
                    # find the callback for subscriptions to this uuid and pass the received message to it
                    self.subscriptions[sub_message['uuid']][device](sub_message)

    def send_config(self):
        if not self.connected:
            self.message_queue.append((self.send_config, []))
            return

        leaf = {
            'type': 'CONFIG',
            'uuid': self.uuid,
            'model': self.model,
            'name': self.name,
            'token': self.token,
            'api_version': self.API_VERSION,
        }
        self.socket.send(json.dumps(leaf))

    def subscribe(self, uuid, device, callback):
        if not self.connected:
            self.message_queue.append((self.subscribe, [uuid, device, callback]))
            return

        if uuid not in self.subscriptions:
            self.subscriptions['uuid'] = {}
        self.subscriptions['uuid'][device] = callback

        message = {
            'type': 'SUBSCRIBE',
            'uuid': self.uuid,
            'sub_uuid': uuid,
            'sub_device': device
        }
        self.socket.send(json.dumps(message))

    def send_status(self, device_name):
        if not self.connected:
            self.message_queue.append((self.send_status, [device_name]))
            return

        if isinstance(device_name, Device):
            device = device_name
        else:
            device = self.get_device(device_name)

        if not device:
            return self.send_unknown_device(device_name)

        message = {
            'type': 'DEVICE_STATUS',
            'uuid': self.uuid,
            'device': device.name,
            'format': device.format,
            'value': device.value,
            'mode': device.mode,
            'options': device.options
        }
        self.socket.send(json.dumps(message))

    def get_device(self, device):
        """
        Gets a device or returns a NoDevice if that device is not registered
        :rtype: Device
        """
        return self.devices.get(device, NoDevice())

    def register_device(self, device):
        self.devices[device.name] = device
        device.add_listener(lambda state: self.send_status(state))
        self.send_status(device)

    def process_queue(self):
        assert self.connected, "must be connected to process messages"
        for message in self.message_queue:
            # message are stored as (function, [parameters]) tuples
            message[0](*message[1])
        self.clear_queue()

    def clear_queue(self):
        self.message_queue = []

    @staticmethod
    def is_valid_message(self):
        return True

    def send_unknown_device(self, device_name):
        message = {'uuid': self.uuid,
                   'type': 'UNKNOWN_DEVICE',
                   'device': device_name}
        self.socket.send(json.dumps(message))


class Device:
    IN = "IN"
    OUT = "OUT"

    def __init__(self, name, initial, format, mode=IN, units=None, onchange=None):
        self.name = name
        self._value = initial
        self.format = format
        self.mode = mode
        self.units = units
        self.listeners = set()
        if onchange:
            self.listeners.add(onchange)
        self.options = {'auto': True}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        self._value = new
        if self.listeners and self.options['auto']:
            for callback in self.listeners.copy():
                try:
                    callback(self)
                except:
                    # if there is an invalid callback, remove it
                    self.listeners.remove(callback)

    def add_listener(self, callback):
        self.listeners.add(callback)

    def send_option(self, option, socket):
        pass

    @staticmethod
    def send_invalid_option(message, socket):
        message = {'uuid': message['uuid'],
                   'type': 'INVALID_OPTION',
                   'device': message['device'],
                   'option': message['option']}
        socket.send(json.dumps(message))

    def parse_value(self, value, format=None):
        format = format or self.format

        if format == 'bool':
            accepted_true = [1, '1', True, 'True', 'true']
            accepted_false = [0, '0', False, 'False', 'false']
            if value in accepted_true:
                return 1
            elif value in accepted_false:
                return 0
            else:
                return False
        elif format == 'number' or format == 'number+units':
            try:
                return float(value)
            except ValueError:
                return False
        else:
            return str(value)

    def send_invalid_mode(self, message, socket):
        message = {'uuid': message['uuid'],
                   'type': 'INVALID_MODE',
                   'device': message['device']}
        socket.send(json.dumps(message))

    def set_option(self, option, value):
        if option in self.options:
            self.options[option] = value
            return True
        else:
            return False

    def send_invalid_value(self, message, socket):
        message = {'uuid': message['uuid'],
                   'type': 'INVALID_VALUE',
                   'device': message['device'],
                   'value': message['value']}
        socket.send(json.dumps(message))


class NoDevice(Device):

    def __init__(self):
        super().__init__('NoDevice', False, 'boolean')

    def __bool__(self):
        return False


