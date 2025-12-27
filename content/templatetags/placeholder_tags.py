from django import template

from content.models import InducteePhotoPlaceholder

register = template.Library()


@register.inclusion_tag("tags/inductee_placeholder_image.html")
def inductee_placeholder_image():
    return {
        "placeholder": InducteePhotoPlaceholder.objects.first(),
    }
