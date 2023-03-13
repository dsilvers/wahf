from django.db import models


class MembershipLevel(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    price = models.PositiveSmallIntegerField(
        help_text="Annual price charged for this membership level."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
