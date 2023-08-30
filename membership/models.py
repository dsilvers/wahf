from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from wahf.mixins import OpenGraphMixin


class BanquetRSVPPage(OpenGraphMixin, Page):
    parent_page_type = [
        "content.HomePage",
    ]


class BanquetRSVPThanksPage(OpenGraphMixin, Page):
    parent_page_type = [
        "content.HomePage",
    ]


class BanquetPayment(models.Model):
    stripe_id = models.CharField(max_length=100)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    attendee_names = models.CharField(max_length=250)
    docent_tour = models.CharField(max_length=250)
    signup_date = models.DateTimeField()


class MembershipLevel(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    price = models.PositiveSmallIntegerField(
        help_text="Annual price charged for this membership level, in whole dollars (no cents). Example: 10"
    )

    stripe_price_id = models.CharField(max_length=50, blank=True, null=True)
    allow_recurring_payments = models.BooleanField(default=False)
    is_lifetime = models.BooleanField(default=False)
    is_business = models.BooleanField(default=False)
    includes_spouse = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


@register_snippet
class MembershipJoinSnippet(models.Model):
    title = models.CharField(max_length=250)
    content = RichTextField()
    lifetime_membership_blurb = RichTextField(blank=True)
    credit_card_blurb = models.TextField(blank=True)
    automatic_renewal_blurb = models.TextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("content"),
        FieldPanel("lifetime_membership_blurb"),
        FieldPanel("credit_card_blurb"),
        FieldPanel("automatic_renewal_blurb"),
    ]

    class Meta:
        verbose_name_plural = "Membership Join Page - Content Blocks"

    def __str__(self):
        return "Membership Join Page - Content Blocks"


@register_snippet
class MembershipThanksSnippet(models.Model):
    title = models.CharField(max_length=250)
    content = RichTextField()

    panels = [
        FieldPanel("title"),
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name_plural = "Membership Thanks Page - Content Blocks"

    def __str__(self):
        return "Membership Thanks Page - Content Blocks"


@register_snippet
class MembershipEmailTemplateSnippet(models.Model):
    slug = models.CharField(max_length=200, unique=True)
    subject = models.CharField(max_length=800)
    body = models.TextField()

    panels = [
        FieldPanel("slug"),
        FieldPanel("subject"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"Email Template: {self.slug} - {self.subject}"
