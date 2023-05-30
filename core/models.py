from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200)
    image = models.ImageField(default='default.png', upload_to='media/profile_pics')
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} profile"
