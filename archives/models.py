from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Page

from wahf.mixins import OpenGraphMixin


class Person(ClusterableModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ForeignKey(
        "archives.WAHFImage", null=True, blank=True, on_delete=models.SET_NULL
    )

    name_search = models.CharField(max_length=200, blank=True, default="")

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("image"),
    ]

    class Meta:
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.last_name and self.first_name:
            return f"{self.last_name}, {self.first_name}"
        if self.last_name:
            return self.last_name
        if self.first_name:
            return self.first_name
        return "NO NAME SET"

    autocomplete_search_field = "name_search"

    def autocomplete_label(self):
        return self.name


class Location(ClusterableModel):
    name = models.CharField(max_length=200)
    # airport_code = models.CharField(max_length=200)
    # latitude
    # longitude

    autocomplete_search_field = "name"

    def autocomplete_label(self):
        return self.name


class AircraftType(ClusterableModel):
    name = models.CharField(max_length=200)

    autocomplete_search_field = "name"

    def autocomplete_label(self):
        return self.name

    @classmethod
    def autocomplete_create(kls: type, value: str):
        return kls.objects.create(name=value)


class AircraftTailNumber(ClusterableModel):
    name = models.CharField(max_length=200)

    autocomplete_search_field = "name"

    def autocomplete_label(self):
        return self.name

    @classmethod
    def autocomplete_create(kls: type, value: str):
        return kls.objects.create(name=value)


class WAHFImage(ClusterableModel, AbstractImage):
    caption = models.CharField(max_length=255, blank=True)
    date = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)

    people = models.ManyToManyField(Person, blank=True, verbose_name="People")
    locations = models.ManyToManyField(Location, blank=True, verbose_name="Locations")
    aircraft_type = models.ManyToManyField(
        AircraftType, blank=True, verbose_name="Aircraft Types"
    )
    aircraft_registration = models.ManyToManyField(
        AircraftTailNumber, blank=True, verbose_name="N Numbers"
    )

    admin_form_fields = tuple(
        filter(lambda x: x != "tags", Image.admin_form_fields)
    ) + (
        "caption",
        "source",
        "date",
        "people",
        "locations",
        "aircraft_type",
        "aircraft_registration",
    )


class WAHFRendition(AbstractRendition):
    image = models.ForeignKey(
        WAHFImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class CollectionList(OpenGraphMixin, Page):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["collection_list"] = CollectionGallery.objects.child_of(self).live()
        return context

    parent_page_type = [
        "home.HomePage",
    ]

    subpage_types = [
        "archives.CollectionGallery",
    ]


class CollectionGallery(OpenGraphMixin, Page):
    collection = models.OneToOneField(
        "wagtailcore.collection", on_delete=models.PROTECT
    )
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
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
    description = RichTextField(
        help_text="A longer description of this gallery. Displayed on the gallery detail page."
    )

    content_panels = Page.content_panels + [
        FieldPanel("collection"),
        MultiFieldPanel(
            [
                FieldPanel("date_start"),
                FieldPanel("date_end"),
                FieldPanel("image"),
                FieldPanel("short_description"),
            ],
            heading="Gallery List and Preview Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("description"),
            ],
            heading="Gallery Detail",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["collection_images"] = WAHFImage.objects.filter(
            collection=self.collection
        )

        return context

    parent_page_type = [
        "archives.CollectionList",
    ]
