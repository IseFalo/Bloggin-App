# Assuming this code is in a file called `custom_filters.py` inside one of your Django apps

from django import template
import bleach

register = template.Library()


def remove_tags(value):
    return bleach.clean(value, tags=["b", "i", "p"])

register.filter('remove_tags', remove_tags)