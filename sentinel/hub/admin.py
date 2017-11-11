from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Leaf)
admin.site.register(StringDevice)
admin.site.register(BooleanDevice)
admin.site.register(NumberDevice)
admin.site.register(UnitDevice)