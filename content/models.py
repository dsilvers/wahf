from django.db import models
from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet

from wahf.mixins import OpenGraphMixin


class InducteeListPage(OpenGraphMixin, Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["inductee_list"] = InducteeDetailPage.objects.child_of(self).live()
        return context

    subpage_types = [
        "content.InducteeDetailPage",
    ]

    parent_page_type = [
        "home.HomePage",
    ]

    subpage_types = [
        "content.InducteeDetailPage",
    ]


class InducteeDetailPage(OpenGraphMixin, Page):
    person = models.OneToOneField("archives.Person", on_delete=models.PROTECT)
    tagline = models.TextField(
        blank=True,
        help_text="Short description of the Inductee. This is displayed on the Inductee List page.",
    )

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
    )

    inducted_date = models.DateField(null=True, blank=True)
    born_date = models.DateField(null=True, blank=True)
    died_date = models.DateField(null=True, blank=True)
    born_year = models.PositiveSmallIntegerField(null=True, blank=True)
    died_year = models.PositiveSmallIntegerField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("person"),
        FieldPanel("tagline"),
        FieldPanel("body"),
        FieldPanel("inducted_date"),
        FieldPanel("born_date"),
        FieldPanel("died_date"),
    ]

    parent_page_type = [
        "content.InducteeListPage",
    ]

    def get_graph_image(self):
        if self.person.image:
            return self.person.image
        return super().get_graph_image()


class FreeformPage(OpenGraphMixin, Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


# Menu System
# https://learnwagtail.com/tutorials/how-to-create-a-custom-wagtail-menu-system/
class MenuItem(Orderable):
    menu_label = models.CharField(blank=True, null=True, max_length=50)

    link_url = models.CharField(max_length=500, blank=True)

    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )

    page = ParentalKey("Menu", related_name="menu_items")

    panels = [
        FieldPanel("menu_label"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return "#"

    @property
    def title(self):
        if self.link_page and not self.menu_label:
            return self.link_page.title
        elif self.menu_label:
            return self.menu_label
        return "Missing Title"


@register_snippet
class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)
    # slug = models.SlugField()

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("slug"),
            ],
            heading="Menu",
        ),
        InlinePanel("menu_items", label="Menu Item"),
    ]

    def __str__(self):
        return self.title
