from django.contrib import admin

from .models import *


admin.site.register(Item)

admin.site.register(Discount)

admin.site.register(Tax)

admin.site.register(Order)