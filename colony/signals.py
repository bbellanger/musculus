# colony signals.py
"""
Transfer events information transparently
in-between Mouse and History models
"""

from django.db.models.signals import post_save # Action when save() is triggered
from django.dispatch import receiver           # Decorator that register function as a listener for signal
from .models import Mouse, Litter, History
from datetime import date

@receiver(post_save, sender=Mouse)             # After Mouse is saved, run mouse_birth_history
def mouse_birth_history(sender, instance, created, **kwargs):
    """Create a Birth event when a new mouse is saved for the first time."""
    if created:
        History.objects.create(
            mouse=instance,
            event='birth',
            date=instance.dob or date.today(),
            cage=instance.cage,
            new_status='alive',
            notes='Auto-created on mouse creation.',
        )

@receiver(post_save, sender=Litter)
def litter_history(sender, instance, created, **kwargs):
    """
    When a litter is saved, record a 'litter' event on both parents.
    pup_count is filled in later via litter_update or manually.
    """
    if created:
        mp = instance.mating_pair
        pup_count = instance.pups.count() or None
        for mouse in [mp.male, mp.female]:
            if mouse:
                History.objects.create(
                    mouse=mouse,
                    event='litter',
                    date=instance.dob,
                    litter=instance,
                    mating_pair=mp,
                    pup_count=pup_count,
                )
