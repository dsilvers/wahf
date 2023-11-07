# Generated by Django 4.1.7 on 2023-11-07 05:05

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("archives", "0011_remove_collectiongallery_name"),
        ("content", "0013_alter_articlepage_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="articlepage",
            name="byline",
        ),
        migrations.CreateModel(
            name="ArticleAuthor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "about_blurb",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="A short blurb about this author, to be included at the end of articles that they author.",
                    ),
                ),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Author photo, headshot, or whatever you want to put below their articles.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="archives.wahfimage",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="articlepage",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="content.articleauthor",
            ),
        ),
    ]
