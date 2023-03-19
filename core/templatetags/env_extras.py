import os
from django import template

register = template.Library()

import environ
env = environ.Env()
environ.Env.read_env()

@register.simple_tag
def get_env(key):
    return env(key)