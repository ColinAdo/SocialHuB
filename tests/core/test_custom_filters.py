from django.test import TestCase
from django.contrib.auth.models import User

from core.models import Post, Comment, FollowUnFollow

from core.templatetags.custom_filters import custom_timesince, truncate_word, get_item

from datetime import timedelta

class CustomFiltersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        self.post = Post.objects.create(author=self.user)

    def test_custom_filter_now(self):
        self.assertEquals(custom_timesince(self.post.date_posted), "Just now")

    def test_custom_filter_minute_ago(self):

        one_minute_ago = self.post.date_posted - timedelta(minutes=1)
        result = custom_timesince(one_minute_ago)
        self.assertEqual(result, "a minute ago")

    def test_custom_filter_minutes_ago(self):

        minutes_ago = self.post.date_posted - timedelta(minutes=30)
        result = custom_timesince(minutes_ago)
        self.assertEqual(result, "30 minutes ago")

    def test_filter_hour_ago(self):

        one_hour_ago = self.post.date_posted - timedelta(hours=1)
        result = custom_timesince(one_hour_ago)
        self.assertEqual(result, "an hour ago")

    def test_filter_hours_ago(self):

        hours_ago = self.post.date_posted - timedelta(hours=12)
        result = custom_timesince(hours_ago)
        self.assertEqual(result, "12 hours ago")

    def test_filter_day_ago(self):

        one_day_ago = self.post.date_posted - timedelta(days=1)
        result = custom_timesince(one_day_ago)
        self.assertEqual(result, "a day ago")

    def test_filter_days_ago(self):

        days_ago = self.post.date_posted - timedelta(days=20)
        result = custom_timesince(days_ago)
        self.assertEqual(result, "20 days ago")

    def test_filter_month_ago(self):

        one_month_ago = self.post.date_posted - timedelta(days=30)
        result = custom_timesince(one_month_ago)
        self.assertEqual(result, "a month ago")

    def test_filter_months_ago(self):

        months_ago = self.post.date_posted - timedelta(days=60)
        result = custom_timesince(months_ago)
        self.assertEqual(result, "2 months ago")

    def test_filter_year_ago(self):
        one_year_ago = self.post.date_posted - timedelta(days=365)
        result = custom_timesince(one_year_ago)
        self.assertEqual(result, "a year ago")

    def test_filter_years_ago(self):
        years_ago = self.post.date_posted - timedelta(days=730)
        result = custom_timesince(years_ago)
        self.assertEqual(result, "2 years ago")

class TruncateWordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="TestUser")
        self.post = Post.objects.create(author=self.user)
        self.comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content="This is a comment that can be truncated to shorter phrases"
        )

    def test_truncate_words_when_wordcount_is_in_word_length(self):
        words = truncate_word(self.comment.content, 3)
        result = 'This is a.....'
        self.assertEqual(words, result)

    def test_truncate_words_when_wordcount_is_not_in_word_length(self):
        words = truncate_word(self.comment.content, 12)
        result = self.comment.content
        self.assertEqual(words, result)

    def test_get_item(self):
        follower = User.objects.create(username="Follower")
        followed = User.objects.create(username="Followed")

        social = FollowUnFollow.objects.create(follower=follower, user_being_followed=followed)

        dictionary = {
            social.follower.username: follower.username,
            social.user_being_followed.username: followed.username,
        } 

        follower_name = get_item(dictionary, social.follower.username)
        followed_name = get_item(dictionary, social.user_being_followed.username)
        following_none_name = get_item(dictionary, social.follower)
        followed_none_name = get_item(dictionary, social.user_being_followed)

        self.assertEqual(follower_name, follower.username)
        self.assertEqual(followed_name, followed.username)
        self.assertIsNone(following_none_name, follower.username)
        self.assertIsNone(followed_none_name, followed.username)
