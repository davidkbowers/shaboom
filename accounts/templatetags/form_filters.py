from django import template
from django.forms.widgets import Input

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css_classes):
    """Adds CSS classes to a form field"""
    if hasattr(field, 'field') and hasattr(field.field, 'widget'):
        if not field.field.widget.attrs.get('class'):
            field.field.widget.attrs['class'] = ''
        field.field.widget.attrs['class'] += f' {css_classes}'
        return field
    return field

@register.filter(name='getattr')
def getattr_filter(obj, attr):
    """Gets an attribute of an object dynamically from a string name"""
    return getattr(obj, attr, '')

@register.filter(name='add')
def add_filter(value, arg):
    """Concatenates value and arg"""
    return str(value) + str(arg)
