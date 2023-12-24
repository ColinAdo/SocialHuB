from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from io import BytesIO
from PIL import Image

from core.models import Profile, Post, LikePost, FollowUnFollow, Comment, Message, EmailVerification

import unittest

class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        self.profile = Profile.objects.create(user=self.user, image=self.get_image_file())

    def test_str_returns(self):
        self.assertEquals(self.profile.__str__(), self.profile.user.username+" profile")

    def test_save_method_resizes_image(self):
        img = Image.open(self.profile.image.path)

        self.assertTrue(img.width == 300)
        self.assertTrue(img.height == 300)

    def get_image_file(self, name="test_image.png", ext="png", size=(400, 400), color=(256, 0, 0)):
        file = BytesIO()
        image = Image.new("RGBA", size, color)
        image.save(file, ext)
        file.name = name
        file.seek(0)
        return SimpleUploadedFile(name, file.read())

class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        
        self.post = Post.objects.create(
            author=self.user, 
            file='post_pics/test_unknown.txt'
        )

        self.post_for_image = Post.objects.create(
            author=self.user, 
            file='post_pics/test_image.png'
        )
        
        self.post_for_video = Post.objects.create(
            author=self.user, 
            file='post_pics/test_video.mp4'
        )

    def test_str_returns(self):
        self.assertEquals(self.post.__str__(), self.post.author.username+" posts")

    def test_get_file_type_for_unknown_post(self):
        file_type = self.post.get_file_type()
        self.assertEquals(file_type, "unknown")

    def test_get_file_type_for_image_post(self):
        file_type = self.post_for_image.get_file_type()
        self.assertEquals(file_type, "image")

    @unittest.skip("Still finding best way to test it..")
    def test_get_file_type_for_video_post(self):
        file_type = self.post_for_video.get_file_type()
        self.assertEquals(file_type, "video")


class LikePostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        self.post = Post.objects.create(author=self.user)
        self.like_post = LikePost.objects.create(post_id=self.post, user=self.user)

    def test_str_returns(self):
        self.assertEquals(self.like_post.__str__(), self.post.author.username+" posts likes")

class FollowUnFollowTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="TestUserOne")
        self.user2 = User.objects.create(username="TestUserTwo")
        self.follows = FollowUnFollow.objects.create(follower=self.user1, user_being_followed=self.user2)

    def test_str_returns(self):
        self.assertEquals(self.follows.__str__(), self.user2.username+" followers")

class CommentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        self.post = Post.objects.create(author=self.user)

        self.comment = Comment.objects.create(user=self.user, post=self.post)

    def test_str_returns(self):
        self.assertEquals(self.comment.__str__(), self.post.author.username+" comments")

class MessageTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create(username="Sender")
        self.receiver = User.objects.create(username="Receiver")

        self.message = Message.objects.create(sender=self.sender, receiver=self.receiver)

    def test_str_returns(self):
        self.assertEquals(self.message.__str__(), f"Message From: {self.sender.username} | To: {self.receiver.username}")

class EmailVerificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")

        self.obj = EmailVerification.objects.create(user=self.user)

    def test_str_returns(self):
        self.assertEquals(self.obj.__str__(), self.user.username+" verification code")
