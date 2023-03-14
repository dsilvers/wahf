from django import template

register = template.Library()


@register.inclusion_tag("tags/image_caption.html")
def caption(image, include_title=False):
    if image:
        caption = image.caption
        if include_title:
            if not caption:
                caption = image.title
            else:
                caption = f"{image.caption} [{image.title}]"

        return {
            "caption": caption,
            "source": image.source,
            "date": image.date,
        }
