from django.urls import path
from . import views

urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # Mouse
    path('mouse/create/',        views.mouse_create,    name='mouse_create'),
    path('mouse/<uuid:pk>/update/', views.mouse_update, name='mouse_update'),
    path('mouse/<uuid:pk>/delete/', views.mouse_delete, name='mouse_delete'),
    path('mouse/<uuid:pk>/history/', views.mouse_history, name='mouse_history'),

    # Cage
    path('cage/create/',         views.cage_create,     name='cage_create'),
    path('cage/<int:pk>/update/', views.cage_update,    name='cage_update'),
    path('cage/<int:pk>/delete/', views.cage_delete,    name='cage_delete'),
    path('cage/<int:pk>/animals/', views.cage_animals, name='cage_animals'),

    # Thermal label generation
    path('cages/<int:pk>/label.pdf', views.cage_label_pdf, name='cage_label_pdf'),
    path('cages/<int:pk>/print-label/', views.cage_label_print, name='cage_label_print'),

    # MatingPair
    path('matingpair/create/',          views.matingpair_create, name='matingpair_create'),
    path('matingpair/<int:pk>/update/', views.matingpair_update, name='matingpair_update'),
    path('matingpair/<int:pk>/delete/', views.matingpair_delete, name='matingpair_delete'),

    # Litter
    path('litter/create/',          views.litter_create, name='litter_create'),
    path('litter/<int:pk>/update/', views.litter_update, name='litter_update'),
    path('litter/<int:pk>/delete/', views.litter_delete, name='litter_delete'),
]
