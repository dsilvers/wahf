# Generated by Django 4.1.7 on 2023-03-20 04:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0012_user_uuid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="renewal_payment_date",
        ),
        migrations.AddField(
            model_name="user",
            name="last_payment_date",
            field=models.DateField(
                blank=True,
                help_text="The date they last paid their membership dues.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="membership_expiry_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
