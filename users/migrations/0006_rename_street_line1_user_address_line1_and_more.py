# Generated by Django 4.1.7 on 2023-03-13 01:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_user_spouse_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="street_line1",
            new_name="address_line1",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="street_line2",
            new_name="address_line2",
        ),
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, default="", max_length=100),
            preserve_default=False,
        ),
    ]
