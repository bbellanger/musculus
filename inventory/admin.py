from django.contrib import admin
from .models import Manufacturer, Category, Vendor, Order, OrderItems, Item

admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(Vendor)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(Item)
