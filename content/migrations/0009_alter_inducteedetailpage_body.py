# Generated by Django 4.1.7 on 2023-07-15 01:00

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0008_alter_inducteedetailpage_gallery"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inducteedetailpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="title")),
                    ("paragraph", wagtail.blocks.RichTextBlock()),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
    ]
