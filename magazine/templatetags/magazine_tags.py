from django import template

from magazine.models import MagazineIssuePage

register = template.Library()


@register.simple_tag()
def get_current_magazine_issue():
    return MagazineIssuePage.objects.live().order_by("-date").first()
