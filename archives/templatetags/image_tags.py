from django import template

register = template.Library()


@register.inclusion_tag("tags/image_caption.html")
def caption(image):
    if image:
        return {
            "caption": image.caption,
            "source": image.source,
            "date": image.date,
        }
