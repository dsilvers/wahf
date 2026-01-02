from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class OpenGraphMixin(models.Model):
    og_image = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Social media image (1200x630px recommended)",
    )

    og_image_square = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Square social media image (1080x1080 recommended)",
    )

    # Add the field to the Promote tab
    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("og_image"),
                FieldPanel("og_image_square"),
            ],
            heading="Social Media Metadata",
        )
    ]

    def get_graph_image(self):
        return self.og_image

    def get_graph_description(self):
        return self.search_description if self.search_description else ""

    class Meta:
        abstract = True
