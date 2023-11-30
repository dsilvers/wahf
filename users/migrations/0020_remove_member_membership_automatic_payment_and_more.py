# Generated by Django 4.2.7 on 2023-11-29 15:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_member_membership_join_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="membership_automatic_payment",
        ),
        migrations.AddField(
            model_name="member",
            name="stripe_subscription_active",
            field=models.BooleanField(default=False),
        ),
    ]
