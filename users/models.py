import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must be staff.")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must be a superuser.")
        return self.create_user(email, password, **kwargs)


class User(AbstractUser):
    username = None
    email = models.EmailField("Email Address", unique=True)

    membership_level = models.ForeignKey(
        "membership.MembershipLevel", on_delete=models.PROTECT, blank=True, null=True
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
    membership_automatic_payment = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=50, blank=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    # Inherited from AbstractUser
    #   first_name
    #   last_name
    business_name = models.CharField(max_length=200, blank=True)
    spouse_name = models.CharField(max_length=200, blank=True)

    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = USStateField(blank=True)
    zip = USZipCodeField(blank=True)

    phone = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def name(self):
        if self.business_name:
            return f"{self} ({self.business_name})"
        return str(self)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name

        return self.email

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name"),
                        FieldPanel("last_name"),
                    ]
                ),
                FieldPanel("business_name"),
                FieldPanel("spouse_name"),
                FieldPanel("address_line1"),
                FieldPanel("address_line2"),
                FieldRowPanel(
                    [
                        FieldPanel("city"),
                        FieldPanel("state"),
                        FieldPanel("zip"),
                    ]
                ),
                FieldPanel("phone"),
            ],
            heading="Contact Details",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("membership_level"),
                        FieldPanel("last_payment_date"),
                        FieldPanel("membership_expiry_date"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("stripe_customer_id"),
                        FieldPanel("stripe_subscription_id"),
                        FieldPanel("membership_automatic_payment"),
                    ]
                ),
            ],
            heading="Membership",
        ),
    ]
