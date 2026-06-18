# colony/signals.py
"""
Transfer events information transparently
in-between Mouse and History models
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import History
from django.utils import timezone


#@receiver(pre_save, sender='colony.Mouse')
#def _capture_old_cage(sender, instance, **kwargs):
#    """Store previous cage_id on the instance before the write so post_save can compare."""
#    if instance.pk:
#        try:
#            instance._old_cage_id = sender.objects.get(pk=instance.pk).cage_id
#        except sender.DoesNotExist:
#            instance._old_cage_id = None
#    else:
#        instance._old_cage_id = None



#@receiver(post_save, sender='colony.Mouse')
#def _log_mouse_history(sender, instance, created, **kwargs):
#    """
#    Write History records automatically:
#      - 'birth' on first save (created=True)
#      - 'move'  whenever cage_id changes on an existing mouse
#    """
#    if created:
#        History.objects.create(
#            mouse=instance,
#            event='birth',
#            date=instance.dob or timezone.now().date(),
#            cage=instance.cage,
#            litter=instance.litter if instance.litter_id else None,
#            new_status='alive',
#        )
#    else:
#        old_cage = getattr(instance, '_old_cage_id', None)
#        new_cage = instance.cage_id
#        if old_cage != new_cage and new_cage is not None:
#            History.objects.create(
#                mouse=instance,
#                event='move',
#                date=timezone.now().date(),
#                cage=instance.cage,
#            )

@receiver(pre_save, sender='colony.Mouse')
def _capture_old_values(sender, instance, **kwargs):
    """Capture cage and status before save so post_save can detect changes."""
    if instance.pk:
        try:
            old = sender.objects.select_related('cage').get(pk=instance.pk)
            instance._old_cage_id = old.cage_id
            instance._old_cage    = old.cage
            instance._old_status  = old.status
        except sender.DoesNotExist:
            instance._old_cage_id = None
            instance._old_cage    = None
            instance._old_status  = None
    else:
        instance._old_cage_id = None
        instance._old_cage    = None
        instance._old_status  = None


@receiver(post_save, sender='colony.Mouse')
def _log_mouse_history(sender, instance, created, **kwargs):
    if created:
        History.objects.create(
            mouse=instance,
            event='birth',
            date=instance.dob or timezone.now().date(),
            cage=instance.cage,
            litter=instance.litter if instance.litter_id else None,
            new_status='alive',
        )
    else:
        old_cage   = getattr(instance, '_old_cage_id', None)
        old_status = getattr(instance, '_old_status',  None)
        new_cage   = instance.cage_id
        new_status = instance.status

        if old_cage != new_cage and new_cage is not None:
            old_cage_obj = getattr(instance, '_old_cage', None)
            old_label    = old_cage_obj.cage_id if old_cage_obj else '—'
            new_label    = instance.cage.cage_id if instance.cage else '—'
            History.objects.create(
                mouse=instance,
                event='move',
                date=timezone.now().date(),
                cage=instance.cage,
                notes=f"Moved from cage {old_label} to cage {new_label}",
            )

        if old_status != new_status and new_status:
            History.objects.create(
                mouse=instance,
                event='status',
                date=timezone.now().date(),
                new_status=new_status,
                notes=f"Status changed from {old_status} to {new_status}",
            )

@receiver(post_save, sender='colony.Litter')
def _log_litter_history(sender, instance, created, **kwargs):
    """
    When a new litter is saved, write a 'litter' event on both parents.
    """
    if created and instance.mating_pair:
        mp = instance.mating_pair
        for parent in [mp.male, mp.female]:
            if parent:
                History.objects.create(
                    mouse=parent,
                    event='litter',
                    date=instance.dob,
                    litter=instance,
                    pup_count=instance.pups.count() or None,
                )
