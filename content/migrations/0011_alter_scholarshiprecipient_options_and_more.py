# Generated by Django 4.1.7 on 2023-10-14 17:56

import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0010_scholarshippage_scholarshiprecipient"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="scholarshiprecipient",
            options={"ordering": ["-year", "scholarship_name"]},
        ),
        migrations.RemoveField(
            model_name="scholarshippage",
            name="contribute_link",
        ),
        migrations.AddField(
            model_name="scholarshippage",
            name="bottom_images",
            field=wagtail.fields.StreamField(
                [("image", wagtail.images.blocks.ImageChooserBlock())],
                blank=True,
                use_json_field=True,
            ),
        ),
    ]