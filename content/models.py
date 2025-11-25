import datetime

from django.db import models
from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtailautocomplete.edit_handlers import AutocompletePanel

from archives.models import Person
from content.blocks import BlockQuoteBlock
from wahf.mixins import OpenGraphMixin


class ArticleAuthor(models.Model):
    name = models.CharField(max_length=255)
    about_blurb = RichTextField(
        help_text="A short blurb about this author, to be included at the end of articles that they author.",
        blank=True,
    )
    contact_email = models.EmailField(blank=True)
    image = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Author photo, headshot, or whatever you want to put below their articles.",
    )

    def __str__(self):
        return self.name


class ArticleListPage(OpenGraphMixin, Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["articles_list"] = (
            ArticlePage.objects.child_of(self)
            .live()
            .select_related("author")
            .order_by("-website_publish_date", "-pk")
        )
        return context

    subpage_types = [
        "content.ArticlePage",
    ]

    parent_page_type = [
        "home.HomePage",
    ]


class KohnProjectPage(Page):
    funding_percent_raised = models.FloatField(null=True, blank=True)
    fundraising_status = RichTextField(
        help_text="The description of the fundraising status of our project.",
        blank=True,
    )

    show_donors_list = models.BooleanField(default=False)

    business_donors = RichTextField(
        help_text="A list of businesses that have donated.",
        blank=True,
    )

    individual_donors = RichTextField(
        help_text="A list of individuals that have donated.",
        blank=True,
    )

    silent_auction_donors = RichTextField(
        help_text="A list of individuals that donated items to the silent auction.",
        blank=True,
    )

    special_donors = RichTextField(
        help_text="A list of special donors to be featured at the top of the page.",
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("funding_percent_raised"),
                FieldPanel("fundraising_status"),
            ],
            heading="Funding Status",
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_donors_list"),
                FieldPanel("special_donors"),
                FieldPanel("business_donors"),
                FieldPanel("individual_donors"),
                FieldPanel("silent_auction_donors"),
            ],
            heading="Donors",
        ),
    ]

    parent_page_type = [
        "home.HomePage",
    ]


class ArticlePage(OpenGraphMixin, Page):
    author = models.ForeignKey(
        "content.ArticleAuthor", null=True, blank=True, on_delete=models.PROTECT
    )
    date = models.DateField(
        null=True,
        blank=True,
        help_text="The date this article was published somewhere. Only displayed on the website.",
    )
    website_publish_date = models.DateField(
        null=True,
        blank=True,
        default=datetime.date.today,
        db_index=True,
        help_text="This date is used for sorting the articles on the website. It is not displayed on the website.",
    )

    image = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Thumbnail and social media preview image for this gallery.",
    )
    short_description = models.TextField(
        help_text="A short description of this gallery, used for gallery list page and social media preview."
    )
    top_badge = models.TextField(
        help_text="A short tag placed over the image. Example 'WAHF: 40 YEARS, 40 STORIES",
        blank=True,
        null=True,
    )

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            (
                "paragraph",
                blocks.RichTextBlock(
                    # features=["bold", "italic", "link", "text-highlight"]
                ),
            ),
            ("image", ImageChooserBlock()),
            ("blockquote", BlockQuoteBlock()),
        ],
        use_json_field=True,
    )

    page_css = models.TextField(
        "CSS/Style",
        blank=True,
        help_text="Leave blank if you do not have any custom CSS. This is custom styling for this article.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("date"),
                FieldPanel("website_publish_date"),
                FieldPanel("image"),
                FieldPanel("short_description"),
                FieldPanel("top_badge"),
            ],
            heading="Details and Preview",
        ),
        MultiFieldPanel(
            [
                FieldPanel("body"),
            ],
            heading="Article Contents",
        ),
        MultiFieldPanel(
            [
                FieldPanel("page_css"),
            ],
            heading="Article Style",
        ),
    ]

    parent_page_type = [
        "home.ArticleListPage",
    ]

    class Meta:
        ordering = ["-website_publish_date", "-pk"]

    def get_graph_image(self):
        if self.image:
            return self.image
        return super().get_graph_image()


class ScholarshipPage(OpenGraphMixin, Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("body"),
            ],
            heading="Page Content",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["scholarship_list"] = ScholarshipRecipient.objects.select_related(
            "image"
        ).all()

        context["top_images"] = []
        context["bottom_images"] = []

        count = 0
        for recipient in context["scholarship_list"]:
            if recipient.image:
                if count % 2 == 0:
                    context["top_images"].append(recipient.image)
                else:
                    context["bottom_images"].append(recipient.image)
                count += 1

        return context

    parent_page_type = [
        "home.ArticleListPage",
    ]


class ScholarshipRecipient(models.Model):
    year = models.PositiveSmallIntegerField(help_text="example: 2023")
    scholarship_name = models.CharField(
        max_length=250, help_text="example: 'Test Person Scholarship'"
    )
    recipient_name = models.CharField(max_length=150)

    blurb = RichTextField(
        help_text="A longer description of this gallery. Displayed on the gallery detail page."
    )

    image = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Scholarship recipient photo.",
    )

    def __str__(self):
        return f"{self.year} {self.scholarship_name} - {self.recipient_name}"

    class Meta:
        ordering = ["-year", "scholarship_name"]


class InducteeListPage(OpenGraphMixin, Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["inductee_list"] = (
            InducteeDetailPage.objects.child_of(self)
            .select_related("person", "photo")
            .order_by("person__last_name", "person__first_name")
            .live()
        )

        return context

    subpage_types = [
        "content.InducteeDetailPage",
    ]

    parent_page_type = [
        "home.HomePage",
    ]


class InducteeDetailPage(OpenGraphMixin, Page):
    # Person is used for sorting, and will typically be the first assigned value for people
    person = models.OneToOneField(
        "archives.Person", on_delete=models.PROTECT, null=True, blank=True
    )
    people = ParentalManyToManyField("archives.Person", related_name="inductee_people")

    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="If multiple people are set above, you can customize thei name that is displayed here.",
    )

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
        blank=True,
    )

    photo = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Main image for the inductee list and primary photo for their page.",
        db_index=True,
    )

    gallery = StreamField(
        [
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        default=[],
        blank=True,
    )

    inducted_date = models.DateField(null=True, blank=True)
    born_date = models.DateField(null=True, blank=True)
    died_date = models.DateField(null=True, blank=True)
    born_year = models.PositiveSmallIntegerField(null=True, blank=True)
    died_year = models.PositiveSmallIntegerField(null=True, blank=True)

    content_panels = Page.content_panels + [
        AutocompletePanel("people", target_model=Person),
        FieldPanel("name"),
        FieldPanel("tagline"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel(
                    "photo",
                    help_text="Hot top: don't set this when creating a new Inductee page, it will automatically copy their image from their Person profile. Main photo for Inductee page. Used for social media sharing and the image at the top of the page.",
                ),
                FieldPanel("gallery"),
            ],
            heading="Photos",
        ),
        MultiFieldPanel(
            [
                FieldPanel("inducted_date"),
                FieldPanel("born_date"),
                FieldPanel("died_date"),
            ],
            heading="Dates",
        ),
    ]

    parent_page_type = [
        "content.InducteeListPage",
    ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        skip_populate_image = kwargs.pop("skip_populate_image", None)

        # Assign a primary person for sorting behaviors
        if not self.person:
            self.person = self.people.first()

        # Assign a default name if one is not set and a person is assigned
        if self.person and self.name == "":
            self.name = f"{self.person.first_name} {self.person.last_name}".strip()

        # Copy the image from the person if one is not set
        if self.person and self.person.image and not self.photo:
            self.photo = self.person.image

        # Update the image on the associated person
        if not skip_populate_image:
            original_page = InducteeDetailPage.objects.get(pk=self.pk)
            if (
                original_page
                and original_page.photo
                and self.photo
                and original_page.photo != self.photo
                and self.person
                and (not self.person.image or self.person.image == original_page.photo)
            ):
                self.person.image = self.photo
                self.person.save(skip_populate_image=True)

        super().save()

    def get_graph_image(self):
        if self.person.image:
            return self.person.image
        return super().get_graph_image()


@register_snippet
class InducteePhotoPlaceholder(models.Model):
    image = models.ForeignKey(
        "archives.WAHFImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Placeholder image for inductees that are missing an image.",
    )

    panels = [
        FieldPanel("image"),
    ]

    class Meta:
        verbose_name_plural = "Inductees List - Missing Photo Placeholder Image"

    def __str__(self):
        return "Inductee Missing Photo Placeholder Image"


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
