from django.template import Library

register = Library()

@register.filter
def get_first_word(value):
    return value.split()[0]


@register.filter(name="truncate_word")
def truncate_word(value, num_words):
    words = value.split()
    if len(words) <= num_words:
        return value
    truncated_words = ' '.join(words[:num_words]) +'...'
    return truncated_words