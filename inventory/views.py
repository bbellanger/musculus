from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Manufacturer, Category, Vendor, Order, OrderItems, Item


# ── Shared context helper ──────────────────────────────────────────────────

def _base_context():
    return {
        'orders':        Order.objects.select_related('requested_by').prefetch_related('orderitems_set__item').all(),
        'items':         Item.objects.select_related('manufacturer', 'category', 'vendor').all(),
        'manufacturers': Manufacturer.objects.all(),
        'categories':    Category.objects.all(),
        'vendors':       Vendor.objects.all(),
        'users':         User.objects.all(),
        'unit_choices':  OrderItems.UNIT_CHOICES,
    }


def _fk(model, pk_str):
    if pk_str:
        return model.objects.filter(pk=pk_str).first()
    return None


# ── Index ──────────────────────────────────────────────────────────────────

@login_required
def index(request):
    return render(request, 'inventory/index.html', _base_context())


# ── Order CRUD ─────────────────────────────────────────────────────────────

@login_required
def order_create(request):
    if request.method == 'POST':
        Order.objects.create(
            name         = request.POST.get('name', ''),
            requested_by = _fk(User, request.POST.get('requested_by')),
        )
    return redirect('inventory:index')


@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.name         = request.POST.get('name', '')
        order.requested_by = _fk(User, request.POST.get('requested_by'))
        order.save()
    return redirect('inventory:index')


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
    return redirect('inventory:index')


# ── OrderItems CRUD ────────────────────────────────────────────────────────

#@login_required
#def orderitem_create(request, order_pk):
#    order = get_object_or_404(Order, pk=order_pk)
#    if request.method == 'POST':
#        item = _fk(Item, request.POST.get('item'))
#        if item:
            # Enrich the item catalog entry with any new info provided
#            manufacturer  = _fk(Manufacturer, request.POST.get('manufacturer'))
#            vendor        = _fk(Vendor, request.POST.get('vendor'))
#            catalog_number = request.POST.get('catalog_number', '').strip()
#            changed = False
#            if manufacturer and not item.manufacturer:
#                item.manufacturer = manufacturer
#                changed = True
#            if vendor and not item.vendor:
#                item.vendor = vendor
#                changed = True
#            if catalog_number and not item.catalog_number:
#                item.catalog_number = catalog_number
#                changed = True
#            if changed:
#                item.save()
#
#            OrderItems.objects.create(
#                item      = item,
#                size_unit = request.POST.get('size_unit') or 1,
#                unit      = request.POST.get('unit', ''),
#                price     = request.POST.get('price', ''),
#                comment   = request.POST.get('comment', ''),
#                order     = order,
#            )
#    return redirect('inventory:index')
@login_required
def orderitem_create(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == 'POST':
        item = _fk(Item, request.POST.get('item'))
        if item:
            manufacturer   = _fk(Manufacturer, request.POST.get('manufacturer'))
            vendor         = _fk(Vendor, request.POST.get('vendor'))
            catalog_number = request.POST.get('catalog_number', '').strip()
            changed = False
            if manufacturer and not item.manufacturer:
                item.manufacturer = manufacturer
                changed = True
            if vendor and not item.vendor:
                item.vendor = vendor
                changed = True
            if catalog_number and not item.catalog_number:
                item.catalog_number = catalog_number
                changed = True
            if changed:
                item.save()

            price_str = request.POST.get('price', '').strip()
            qty_str   = request.POST.get('quantity', '').strip()

            try:
                price_val = float(price_str) if price_str else 0.0
            except ValueError:
                price_val = 0.0

            try:
                quantity = int(qty_str) if qty_str else 1
            except ValueError:
                quantity = 1

            full_amount = round(price_val * quantity, 2) if price_val else None

            OrderItems.objects.create(
                item        = item,
                size_unit   = request.POST.get('size_unit') or 1,
                unit        = request.POST.get('unit', ''),
                quantity    = quantity,
                price       = price_str or '',
                full_amount = full_amount,
                comment     = request.POST.get('comment', ''),
                order       = order,
            )
    return redirect('inventory:index')

@login_required
def orderitem_delete(request, pk):
    oi = get_object_or_404(OrderItems, pk=pk)
    if request.method == 'POST':
        oi.delete()
    return redirect('inventory:index')


# ── Item CRUD ──────────────────────────────────────────────────────────────

@login_required
def item_create(request):
    if request.method == 'POST':
        Item.objects.create(
            name                = request.POST.get('name', ''),
            chemical_formula    = request.POST.get('chemical_formula', ''),
            manufacturer        = _fk(Manufacturer, request.POST.get('manufacturer')),
            category            = _fk(Category, request.POST.get('category')),
            vendor              = _fk(Vendor, request.POST.get('vendor')),
            catalog_number      = request.POST.get('catalog_number', ''),
            manufacturer_number = request.POST.get('manufacturer_number', ''),
            comment             = request.POST.get('comment', ''),
        )
    return redirect('inventory:index')


@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.name                = request.POST.get('name', '')
        item.chemical_formula    = request.POST.get('chemical_formula', '')
        item.manufacturer        = _fk(Manufacturer, request.POST.get('manufacturer'))
        item.category            = _fk(Category, request.POST.get('category'))
        item.vendor              = _fk(Vendor, request.POST.get('vendor'))
        item.catalog_number      = request.POST.get('catalog_number', '')
        item.manufacturer_number = request.POST.get('manufacturer_number', '')
        item.comment             = request.POST.get('comment', '')
        item.save()
    return redirect('inventory:index')


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect('inventory:index')
