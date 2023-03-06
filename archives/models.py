from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class Person(ClusterableModel):
    name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    image = models.ForeignKey(
        "archives.WAHFImage", null=True, blank=False, on_delete=models.SET_NULL
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("image"),
    ]

    class Meta:
        verbose_name_plural = "People"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    autocomplete_search_field = "name"

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
