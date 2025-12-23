from django import template

register = template.Library()


@register.simple_tag()
def stripe_public_key():
    from membership.utils import get_stripe_public_key

    return get_stripe_public_key()
