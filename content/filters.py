import django_filters
from django.db.models import Count
from wagtail.admin.filters import WagtailFilterSet

from content.models import InducteeDetailPage


class LocationTaggedStatusFilter(django_filters.ChoiceFilter):
    """A custom filter to find pages that are untagged."""

    # Define the choices for the dropdown
    CHOICES = [
        ("has_locations", "Has Location"),
        ("no_locations", "No Location"),
    ]

    def __init__(self, *args, **kwargs):
        # We pass the CHOICES list to the parent ChoiceFilter's constructor
        kwargs["choices"] = self.CHOICES
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        # 1. Annotate the queryset with the count of related tags ('tagged_items' is the related_name)
        qs = qs.annotate(location_count=Count("location_tag_page"))

        # 2. Apply the filtering based on the choice selected
        if value == "no_locations":
            # Pages where the tag count is zero
            return qs.filter(location_count=0)
        elif value == "has_locations":
            # Pages where the tag count is greater than zero
            return qs.filter(location_count__gt=0)

        return qs


class InducteeDetailPageFilterSet(WagtailFilterSet):
    # Register the custom filter
    tag_status = LocationTaggedStatusFilter(
        field_name="tags",  # Use the tags field name here for clarity
        label="Location Status",
    )

    class Meta:
        model = InducteeDetailPage
        # Include your custom filter and any other standard filters you want (e.g., live status)
        fields = ["tag_status", "live"]
