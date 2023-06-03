from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import uuid

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} profile"

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_pics')
    caption = models.CharField(max_length=200)
    date_posted = models.DateTimeField(default=timezone.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.username} posts"
    
class LikePost(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)