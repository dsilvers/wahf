from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag()
def stripe_public_key():
    if settings.STRIPE_LIVE_MODE:
        if not settings.STRIPE_LIVE_PUBLIC_KEY:
            raise Exception("STRIPE_LIVE_PUBLIC_KEY not set")
        return settings.STRIPE_LIVE_PUBLIC_KEY

    if not settings.STRIPE_TEST_PUBLIC_KEY:
        raise Exception("STRIPE_TEST_PUBLIC_KEY not set")
    return settings.STRIPE_TEST_PUBLIC_KEY
