# Generated by Django 4.1.7 on 2023-03-14 03:28

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("archives", "0009_rename_wahfcollectiongallery_collectiongallery_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectiongallery",
            name="image",
            field=models.ForeignKey(
                blank=True,
                help_text="Thumbnail and social media preview image for this gallery.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="archives.wahfimage",
            ),
        ),
        migrations.AddField(
            model_name="collectiongallery",
            name="short_description",
            field=models.TextField(
                default="",
                help_text="A short description of this gallery, used for gallery list page and social media preview.",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="collectiongallery",
            name="description",
            field=wagtail.fields.RichTextField(
                help_text="A longer description of this gallery. Displayed on the gallery detail page."
            ),
        ),
    ]
