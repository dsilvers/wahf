import uuid

from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
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
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, blank=True, null=True)
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    attendee_names = models.CharField(max_length=250, blank=True, null=True)
    docent_tour = models.CharField(max_length=250)
    signup_date = models.DateTimeField()


class Member(models.Model):
    membership_level = models.ForeignKey(
        "membership.MembershipLevel", on_delete=models.PROTECT, blank=True, null=True
    )

    membership_join_date = models.DateField(
        blank=True,
        null=True,
        help_text="The date they joined WAHF.",
    )

    last_payment_date = models.DateField(
        blank=True,
        null=True,
        help_text="The date they last paid their membership dues.",
    )
    membership_expiry_date = models.DateField(
        blank=True,
        null=True,
    )

    membership_renewal_reminder_date = models.DateField(
        blank=True,
        null=True,
    )

    stripe_customer_id = models.CharField(max_length=50, blank=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True)
    stripe_subscription_active = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    email = models.EmailField("Email Address", unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    business_name = models.CharField(max_length=200, blank=True)
    spouse_name = models.CharField(max_length=200, blank=True)

    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = USStateField(blank=True)
    zip = USZipCodeField(blank=True)

    phone = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name

        return "*Name Not Set*"


class MemberSignupLog(models.Model):
    signup_datetime = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)


class MembershipLevel(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)

    description = models.TextField(blank=True, null=True)

    price = models.PositiveSmallIntegerField(
        help_text="Annual price charged for this membership level, in whole dollars (no cents). Example: 10"
    )

    price_display = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    stripe_price_id = models.CharField(
        max_length=50, blank=True, null=True, help_text="Recurring payment ID"
    )
    stripe_price_id_one_time = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="One-time (non-automatic) price ID",
    )

    allow_recurring_payments = models.BooleanField(default=False)
    is_lifetime = models.BooleanField(default=False)
    is_business = models.BooleanField(default=False)
    includes_spouse = models.BooleanField(default=False)

    show_on_membership_page = models.BooleanField(default=True)
    membership_page_icon = models.CharField(max_length=50, null=True, blank=True)
    membership_page_sequence = models.PositiveSmallIntegerField(default=99)
    membership_page_text_class = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["membership_page_sequence"]


class MembershipContributionType(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    link = models.CharField(max_length=250, null=True, blank=True)
    sequence = models.PositiveSmallIntegerField(default=99)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sequence"]


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
class MembershipRenewThanksSnippet(models.Model):
    title = models.CharField(max_length=250)
    content = RichTextField()

    panels = [
        FieldPanel("title"),
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name_plural = "Membership Renew Thanks Page - Content Blocks"

    def __str__(self):
        return "Membership Renew Thanks Page - Content Blocks"


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
