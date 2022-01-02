from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='error_truncate')
def error_truncate(error):
    return error[0]
