import uuid

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


class MembershipRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    member = models.ForeignKey(
        "users.Member", null=True, blank=True, on_delete=models.CASCADE
    )


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
