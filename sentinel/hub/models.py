from django.db import models
from channels import Group
import json

class Leaf(models.Model):
	hub_id = 1
	name=models.CharField(max_length=100)
	model=models.CharField(max_length=100)
	uuid=models.CharField(primary_key=True, max_length=36)
	api_version=models.CharField(max_length=10)
	isConnected=models.BooleanField(default=True)

	def set_name(self, name):
		message = self.message_template
		message["type"] = "SET_NAME"
		message["name"] = name
		self.send_message(message)

	def set_option(self, device, option, value):
		message = self.message_template
		message["type"] = "SET_OPTION"
		message["device"] = device
		message["option"] = option
		message["value"] = value
		self.send_message(message)

	def set_output(self, device, value):
		message = self.message_template
		message["type"] = "SET_OUTPUT"
		message["device"] = device
		message["value"] = value
		self.send_message(message)

	def get_option(self, device, option, update=True):
		if update:
			self.refresh_option(device, option)
		#TODO: Replace following code with real code, add option
		return self.device_set.get(name=device).option_set.filter(name=option)

	def get_options(self, device, update=True):
		if update:
			self.refresh_options()
		return self.device_set.get(name=device).option_set.all()

	def get_device(self, device, update=True):
		if update:
			self.refresh_device(device)
		return self.get_devices(False)[device]

	def get_devices(self, update=True):
		if update:
			self.refresh_devices()
		device_sets = [self.booleandevice_set, self.stringdevice_set,\
					  self.numberdevice_set, self.unitdevice_set]
		devices = {}
		for device_set in device_sets:
			for device in device_set.all():
				devices[device.name] = device

		return devices

	def get_name(self):
		return self.name

	def refresh_devices(self):
		message = self.message_template
		message["type"] = "LIST_DEVICES"
		self.send_message(message)

	def refresh_name(self):
		message = self.message_template
		message["type"] = "GET_NAME"
		self.send_message(message)

	def refresh_options(self):
		message = self.message_template
		message["type"] = "LIST_OPTIONS"
		self.send_message(message)

	def refresh_device(self, device):
		message = self.message_template
		message["type"] = "GET_DEVICE"
		message["device"] = device
		self.send_message(message)

	def refresh_option(self, device, option):
		message = self.message_template
		message["type"] = "GET_OPTION"
		message["option"] = option
		message["device"] = device
		self.send_message(message)

	def send_message(self, message, callback=lambda message: None):
		message = {"text":json.dumps(message)}
		Group(self.uuid).send(message)
	
	def create_device(self, device_name, format):
		if format == 'bool':
			device = BooleanDevice(name=device_name, leaf=self, value=False)
		elif format == 'number+units':
			device = UnitDevice(name=device_name, leaf=self, value=0, units="None")
		elif format == 'number':
			device = NumberDevice(name=device_name, leaf=self, value=0)
		else:
			#treat unknown formats as strings per API
			devive = StringDevice(name=device_name, leaf=self, value="")
		return device

	@property
	def message_template(self):
		return {"uuid":self.uuid, "hub_id":self.hub_id}

	def __repr__(self):
		return "Leaf <name: {}, uuid:{}>".format(self.name, self.uuid)

	def __str__(self):
		return repr(self)

class Device(models.Model):
	class Meta:
		abstract = True
	name=models.CharField(max_length=100)
	leaf=models.ForeignKey(Leaf, on_delete=models.CASCADE)

	def update_value(self, message):
		self.value = message['value']

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return "Device <name: {}>".format(self.name)

class StringDevice(Device):
	value=models.CharField(max_length=250)

	@property
	def format(self):
		return "string"

	def __repr__(self):
		return "StringDevice <name:{}, value: {}>".format(self.name, self.value)

class BooleanDevice(Device):
	value=models.BooleanField()

	@property
	def format(self):
		return "bool"

	def __repr__(self):
		return "BooleanDevice <name:{}, value: {}>".format(self.name, self.value)

class NumberDevice(Device):
	value=models.DecimalField(max_digits=15, decimal_places=4)

	@property
	def format(self):
		return "number"

	def __repr__(self):
		return "NumberDevice <name:{}, value: {}>".format(self.name, self.value)

class UnitDevice(Device):
	value=models.DecimalField(max_digits=15, decimal_places=4)
	units=models.CharField(max_length=10)

	def update_value(self, message):
		self.units = message["units"]
		super().update_value(message)

	@property
	def format(self):
		return "number+units"

	def __repr__(self):
		return "UnitDevice <name:{}, value: {}>".format(self.name, self.value)


