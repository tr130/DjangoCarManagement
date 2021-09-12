from django import template

register = template.Library()

@register.filter
def get_quantity(dictionary, key):
    part = dictionary.get(str(key))
    if part:
        return part['quantity']
    else:
        return 0