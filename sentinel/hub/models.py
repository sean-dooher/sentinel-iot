from django.db import models

class Leaf(models.Model):
	name=models.CharField(maxlength=100)
	model=models.CharField(maxlength=100)
	serial=models.IntegerField(primary_key=True)
	isConnected=models.BooleanField()

	def list_sensors(self):
		pass

	def get_name(self):
		pass

	def set_name(self):
		pass

	def get_option(self):
		pass

	def set_option(self):
		pass

	def get_sensor(self):
		pass