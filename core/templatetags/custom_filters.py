from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def custom_timesince(value):
    now = timezone.now()
    diff = now - value

    if diff.days >= 365:
        years = diff.days // 365
        if years == 1:
            return "a year ago"
        return f"{years} years ago"
    elif diff.days >= 30:
        months = diff.days // 30
        if months == 1:
            return "a month ago"
        return f"{months} months ago"
    elif diff.days > 0:
        if diff.days == 1:
            return "a day ago"
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        if hours == 1:
            return "an hour ago"
        return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        if minutes == 1:
            return "a minute ago"
        return f"{minutes} minutes ago"
    else:
        return "Just now"


@register.filter(name="truncate_word")
def truncate_word(value, num_words):
    words = value.split()
    if len(words) <= num_words:
        return value
    truncated_words = ' '.join(words[:num_words]) +'.....'
    return truncated_words

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)