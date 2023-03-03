from django import template

from ..models import MagazineIssuePage

register = template.Library()


@register.simple_tag()
def get_magazine():
    return MagazineIssuePage.objects.all().first()
