# Generated by Django 4.1.7 on 2023-03-20 02:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("membership", "0006_membershipregistration_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="membershiplevel",
            old_name="stripe_recurring_price_id",
            new_name="stripe_price_id",
        ),
    ]
