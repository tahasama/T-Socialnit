from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Relationship

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Relationship)
def create_relation(sender, instance, created, *args, **kwargs):
    senderx = instance.sender
    receiverx = instance.receiver
    if instance.status == "accepted":
        senderx.friends.add(receiverx.user)
        receiverx.friends.add(senderx.user)
        senderx.save()
        receiverx.save()

@receiver(pre_delete, sender=Relationship)
def delete_relation(sender, instance, *args, **kwargs):
    senderx = instance.sender
    receiverx = instance.receiver
    senderx.friends.remove(receiverx.user)
    receiverx.friends.remove(senderx.user)
    senderx.save()
    receiverx.save()