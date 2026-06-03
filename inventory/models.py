from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Now
#import uuid, re

# Inventory models
class Manufacturer(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=50, null=True, blank=True)
    lookup = models.CharField(max_length=50, null=True, blank=True, db_comment="Lookup url for item search") # lookup url for id search
    rep = models.CharField(max_length=30, null=True, blank=True)
    rep_phone = models.CharField(max_length=15, null=True, blank=True)
    rep_email = models.CharField(max_length=30, null=True, blank=True)
    support_phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Vendor(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=50, null=True, blank=True)
    lookup = models.CharField(max_length=50, null=True, blank=True, db_comment="Lookup url for item search")
    phone = models.CharField(max_length=15, null=True, blank=True)
    rep = models.CharField(max_length=30, null=True, blank=True)
    rep_phone = models.CharField(max_length=15, null=True, blank=True)
    rep_email = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    name = models.CharField(max_length=30)
    placed_on = models.DateField(db_default=Now(), db_comment="Date and time the order was placed, default=Now()")
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #OrderItems = models.ForeignKey('OrderItems', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name

class OrderItems(models.Model):
    UNIT_CHOICES = {"L": "Liter", "g": "Grams", "kg": "Kilograms", "lbs": "Pounds"}
    item        = models.ForeignKey('Item', on_delete=models.CASCADE, null=False, blank=False)
    size_unit   = models.DecimalField(max_digits=5, decimal_places=2)
    unit        = models.CharField(max_length=15, null=True, blank=True, choices=UNIT_CHOICES)
    quantity    = models.PositiveIntegerField(default=1)
    #price       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_comment="$$")
    price = models.CharField(max_length=15, null=True, blank=True, db_comment="$$")
    full_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, db_comment="price x quantity")
    comment     = models.CharField(max_length=250, null=True, blank=True)
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems_set')

    def __str__(self):
        return self.item.name

# Item inherit from orderItem which inherit from Order
class Item(models.Model):
    name = models.CharField(max_length=30)
    chemical_formula = models.CharField(max_length=50, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    #order = models.ForeignKey(order, on_delete=SET_NULL, null=True, blank=True)
    #order_items = models.ForeignKey(OrderItems, on_delete=SET_NULL, null=True, blank=True)
    catalog_number = models.CharField(max_length=20, null=True, blank=True)
    manufacturer_number = models.CharField(max_length=20, null=True, blank=True)
    comment = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name
