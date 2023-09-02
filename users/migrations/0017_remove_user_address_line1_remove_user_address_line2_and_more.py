# Generated by Django 4.1.7 on 2023-05-22 20:00

import uuid

import django.db.models.deletion
import localflavor.us.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("membership", "0008_alter_membershipregistration_data"),
        ("users", "0016_alter_user_stripe_customer_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="address_line1",
        ),
        migrations.RemoveField(
            model_name="user",
            name="address_line2",
        ),
        migrations.RemoveField(
            model_name="user",
            name="business_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="city",
        ),
        migrations.RemoveField(
            model_name="user",
            name="last_payment_date",
        ),
        migrations.RemoveField(
            model_name="user",
            name="membership_automatic_payment",
        ),
        migrations.RemoveField(
            model_name="user",
            name="membership_expiry_date",
        ),
        migrations.RemoveField(
            model_name="user",
            name="membership_level",
        ),
        migrations.RemoveField(
            model_name="user",
            name="phone",
        ),
        migrations.RemoveField(
            model_name="user",
            name="spouse_name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="state",
        ),
        migrations.RemoveField(
            model_name="user",
            name="stripe_customer_id",
        ),
        migrations.RemoveField(
            model_name="user",
            name="stripe_subscription_id",
        ),
        migrations.RemoveField(
            model_name="user",
            name="uuid",
        ),
        migrations.RemoveField(
            model_name="user",
            name="zip",
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_payment_date",
                    models.DateField(
                        blank=True,
                        help_text="The date they last paid their membership dues.",
                        null=True,
                    ),
                ),
                ("membership_expiry_date", models.DateField(blank=True, null=True)),
                ("membership_automatic_payment", models.BooleanField(default=False)),
                ("stripe_customer_id", models.CharField(blank=True, max_length=50)),
                ("stripe_subscription_id", models.CharField(blank=True, max_length=50)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("business_name", models.CharField(blank=True, max_length=200)),
                ("spouse_name", models.CharField(blank=True, max_length=200)),
                ("address_line1", models.CharField(blank=True, max_length=200)),
                ("address_line2", models.CharField(blank=True, max_length=200)),
                ("city", models.CharField(blank=True, max_length=200)),
                ("state", localflavor.us.models.USStateField(blank=True, max_length=2)),
                (
                    "zip",
                    localflavor.us.models.USZipCodeField(blank=True, max_length=10),
                ),
                ("phone", models.CharField(blank=True, max_length=100)),
                (
                    "membership_level",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="membership.membershiplevel",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="member",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]