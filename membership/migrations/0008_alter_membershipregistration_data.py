# Generated by Django 4.1.7 on 2023-03-20 02:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "membership",
            "0007_rename_stripe_recurring_price_id_membershiplevel_stripe_price_id",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="membershipregistration",
            name="data",
            field=models.JSONField(default=dict),
        ),
    ]