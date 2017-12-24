from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Leaf)
admin.site.register(Device)
admin.site.register(Condition)
admin.site.register(ConditionalSubscription)
