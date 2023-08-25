from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from PIL import Image

import uuid
import magic

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            outpu_size = (300, 300)
            img.thumbnail(outpu_size)
            img.save(self.image.path)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_pics', default='default.png')
    caption = models.CharField(max_length=200)
    date_posted = models.DateTimeField(default=timezone.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.username} posts"
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     if self.file.path.endswith('.jpg') or self.file.path.endswith('.png'):
    #         img = Image.open(self.file.path)
    #         if img.height > 300 or img.width > 300:
    #             output_size = (300, 300)
    #             img.thumbnail(output_size)
    #             img.save(self.file.path)

    def get_file_type(self):
        file_path = self.file.path
        mime = magic.from_file(file_path, mime=True)
        if mime.startswith('image'):
            return 'image'
        elif mime.startswith('video'):
            return 'video'
        else:
            return 'unknown'
    
class LikePost(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post_id} likes"
    
class FollowUnFollow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    user_being_followed = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_being_followed} followers"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = 'date_posted'

    def __str__(self):
        return f'{self.post.author} comments'

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_sent = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False, null=True)
    is_read = models.BooleanField(default=False, null=True)

    class Meta:
        get_latest_by = 'date_sent'
        
    def __str__(self):
        return f"Message From: {self.sender.username} | To: {self.receiver.username}"
    
class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} verification code'