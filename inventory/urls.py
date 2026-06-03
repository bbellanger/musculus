from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('',                                views.index,            name='index'),
    # Orders
    path('order/create/',                   views.order_create,     name='order_create'),
    path('order/<int:pk>/update/',          views.order_update,     name='order_update'),
    path('order/<int:pk>/delete/',          views.order_delete,     name='order_delete'),
    # Order line items
    path('order/<int:order_pk>/item/add/',  views.orderitem_create, name='orderitem_create'),
    path('orderitem/<int:pk>/delete/',      views.orderitem_delete, name='orderitem_delete'),
    # Items catalog
    path('item/create/',                    views.item_create,      name='item_create'),
    path('item/<int:pk>/update/',           views.item_update,      name='item_update'),
    path('item/<int:pk>/delete/',           views.item_delete,      name='item_delete'),
]
