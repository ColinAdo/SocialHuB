from django.core.files.storage import default_storage
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(pre_save, sender=Profile)
def delete_old_profile_pic(sender, instance, **kwargs):
    if instance.pk:
        old_profile_picture = Profile.objects.get(pk=instance.pk)
        if old_profile_picture.image != instance.image.name and old_profile_picture.image.name != "default.png":
            default_storage.delete(settings.MEDIA_ROOT +'/' + old_profile_picture.image.name)