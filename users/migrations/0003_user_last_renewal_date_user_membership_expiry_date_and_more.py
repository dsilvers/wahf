# Generated by Django 4.1.7 on 2023-03-12 15:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("membership", "0001_initial"),
        ("users", "0002_user_business_name_user_city_user_phone_user_state_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_renewal_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="membership_expiry_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="membership_level",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="membership.membershiplevel",
            ),
        ),
    ]
