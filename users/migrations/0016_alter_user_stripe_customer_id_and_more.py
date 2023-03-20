# Generated by Django 4.1.7 on 2023-03-20 04:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0015_alter_user_membership_automatic_payment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="stripe_customer_id",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="user",
            name="stripe_subscription_id",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
