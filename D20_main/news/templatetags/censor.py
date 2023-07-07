from django import template

register = template.Library()

censored_words = ('редиска', 'Редиска')


@register.filter()
def censor(value):
    for words in censored_words:
        if words in value:
            censor_words = f"p{''.join(['*' for words in range(len(words))])}"
            value = value.replace(words, censor_words)
    return value
