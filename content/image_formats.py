from django.utils.html import format_html
from wagtail.images.formats import Format, register_image_format


class CaptionedImageFormat(Format):
    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)

        container_classes = ""
        if self.name.endswith("_left"):
            container_classes = "float-left half-width"
        elif self.name.endswith("_right"):
            container_classes = "float-right half-width"
        elif self.name.endswith("_double"):
            container_classes = "double-wide"

        if image.caption:
            source = (
                f" <span class='image-credit'>{ image.source }</span>"
                if image.source
                else ""
            )
            html = f"<div class='article-image-container {container_classes}'>{default_html}<figcaption>{image.caption}{source}</figcaption></div>"
        else:
            # no alt text
            html = f"<div class='article-image-container {container_classes}'>{default_html}</div>"

        return format_html(html)


class SuperWidthCaptionedImageFormat(Format):
    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)

        source = (
            f" <span class='image-credit'>{ image.source }</span>"
            if image.source
            else ""
        )
        caption = image.caption if image.caption else ""

        html = f"<div class='full-width-image'>{default_html}<figcaption>{caption}{source}</figcaption></div>"

        return format_html(html)


register_image_format(
    SuperWidthCaptionedImageFormat(
        "captioned_superwidth",
        "Super width - full page width, captioned",
        "img-fluid",
        "width-1200",
    )
)

register_image_format(
    CaptionedImageFormat(
        "captioned_fullwidth",
        "Full width of column, captioned",
        "img-fluid article-image",
        "width-1200",
    )
)

register_image_format(
    CaptionedImageFormat(
        "captioned_left",
        "Float left, captioned",
        "img-fluid article-image",
        "width-600",
    )
)

register_image_format(
    CaptionedImageFormat(
        "captioned_right",
        "Float right, captioned",
        "img-fluid article-image",
        "width-600",
    )
)

register_image_format(
    CaptionedImageFormat(
        "captioned_double",
        "Double Wide Images, captioned",
        "img-fluid article-image",
        "width-600",
    )
)
