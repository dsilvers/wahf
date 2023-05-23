import uuid
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from localflavor.us.models import USStateField, USZipCodeField

from users.utils import get_wahf_group


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


class Member(models.Model):
    user = models.OneToOneField(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="member",
    )

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
    membership_automatic_payment = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=50, blank=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True)
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

    @property
    def membership_valid(self):
        if self.membership_level.is_lifetime:
            return True

        if (
            self.membership_expiry_date
            and self.membership_expiry_date > timezone.now().date()
        ):
            return True

        return False

    @property
    def membership_expiring(self):
        # membership is expiring soon
        # but don't bug them if they are renewing automatically
        if self.membership_automatic_payment:
            return False

        if self.membership_level.is_lifetime:
            return False

        if (
            self.membership_expiry_date
            and self.membership_valid
            and timezone.now().date()
            >= (self.membership_expiry_date - timedelta(days=30))
        ):
            return True

        return False  # expired or valid, but not within the 30 day window

    def update_wahf_group_membership(self, group=None):
        if group is None:
            group = get_wahf_group()

        if self.membership_valid:
            self.user.groups.add(group)
            return True
        else:
            self.user.groups.remove(group)
            return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep first and last names in sync between user and member models
        try:
            if self.user and (
                self.first_name != self.user.first_name
                or self.last_name != self.user.last_name
                or self.email != self.user.email
            ):
                User.objects.filter(pk=self.user.pk).update(
                    first_name=self.first_name,
                    last_name=self.last_name,
                    email=self.email,
                )
        except Exception:
            pass


class User(AbstractUser):
    username = None
    email = models.EmailField("Email Address", unique=True)

    # Inherited from AbstractUser and sync'd to Member model when it changes
    #   first_name
    #   last_name

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def name(self):
        if self.member and self.member.business_name:
            return f"{self} ({self.member.business_name})"
        return str(self)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name

        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep first and last names in sync between user and member models
        try:
            if self.member and (
                self.first_name != self.member.first_name
                or self.last_name != self.member.last_name
                or self.email != self.member.email
            ):
                Member.objects.filter(pk=self.member.pk).update(
                    first_name=self.first_name,
                    last_name=self.last_name,
                    email=self.email,
                )
        except Exception:
            pass
