# Generated by Django 4.1.7 on 2023-03-12 22:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_remove_user_last_renewal_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="spouse_name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]