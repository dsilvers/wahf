# Generated by Django 4.1.7 on 2023-03-20 04:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_alter_user_membership_automatic_payment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="membership_automatic_payment",
            field=models.BooleanField(default=False),
        ),
    ]