# Generated by Django 4.1.7 on 2023-11-07 01:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0012_remove_scholarshippage_bottom_images_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="articlepage",
            options={"ordering": ["-date"]},
        ),
    ]