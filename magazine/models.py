from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from wahf.mixins import OpenGraphMixin


class MagazineIssuePage(OpenGraphMixin, Page):
    date = models.DateField(
        help_text="Date of issue for this magazine release. Used for sorting issues by date."
    )
    headline = models.TextField(help_text="Headline on the cover of the magazine.")
    blurb = RichTextField(
        help_text="Short snippet of text describing the content inside this issue."
    )
    cover = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Cover image.",
    )
    download_pdf = models.ForeignKey(
        "wagtaildocs.Document",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.headline}"

    def get_graph_image_url(self):
        if self.cover:
            return self.cover.full_url
        return super().get_graph_image_url()

    def get_sitemap_urls(self, request):
        # Individual issues are paywalled and should not appear in sitemaps
        return []

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("headline"),
        FieldPanel("blurb"),
        FieldPanel("cover"),
        FieldPanel("download_pdf"),
    ]

    parent_page_type = [
        "magazine.MagazineListPage",
    ]

    subpage_types = []


class MagazineListPage(OpenGraphMixin, Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["magazine_list"] = (
            MagazineIssuePage.objects.child_of(self).live().order_by("-date")
        )
        return context

    def get_graph_image(self):
        first_magazine = (
            MagazineIssuePage.objects.child_of(self).live().order_by("-date").first()
        )
        if first_magazine:
            return first_magazine.get_graph_image()
        return super().get_graph_image()

    subpage_types = [
        "magazine.MagazineIssuePage",
    ]

    parent_page_type = [
        "content.HomePage",
    ]
