from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from wahf.mixins import OpenGraphMixin


class HomePageCard(models.Model):
    tagline = models.CharField(max_length=255, blank=True)
    heading = models.CharField(max_length=255)
    blurb = RichTextField()
    date = models.DateField(blank=True, null=True)
    image = models.ForeignKey(
        "content.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page", on_delete=models.CASCADE, null=True, blank=True
    )
    link_text = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("tagline"),
        FieldPanel("heading"),
        FieldPanel("blurb"),
        FieldPanel("date"),
        FieldPanel("image"),
        FieldPanel("link_page"),
        FieldPanel("link_text"),
    ]

    class Meta:
        abstract = True


class HomePageCardItem(Orderable, HomePageCard):
    page = ParentalKey(
        "home.HomePage", on_delete=models.CASCADE, related_name="home_page_cards"
    )


class HomePage(OpenGraphMixin, Page):
    non_member_headline = models.TextField()
    non_member_blurb = RichTextField()
    non_member_link_text = models.CharField(max_length=200, blank=True)
    non_member_link_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    non_member_image = models.ForeignKey(
        "content.WAHFImage",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        InlinePanel(
            "home_page_cards", heading="Home Page Cards", label="Home Page Card"
        ),
        MultiFieldPanel(
            [
                FieldPanel("non_member_headline"),
                FieldPanel("non_member_blurb"),
                FieldPanel("non_member_link_text"),
                FieldPanel("non_member_link_page"),
                FieldPanel("non_member_image"),
            ],
            heading="Non Member Splash",
        ),
    ]

    parent_page_type = [
        "wagtailcore.Page",
    ]

    subpage_types = [
        "content.InducteeListPage",
        "magazine.MagazineListPage",
        "content.FreeformPage",
    ]

    def get_graph_image(self):
        if self.non_member_image:
            return self.non_member_image
        return super().get_graph_image()
