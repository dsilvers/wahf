# Generated by Django 4.1.7 on 2023-03-14 04:27

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models

import wahf.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0083_workflowcontenttype"),
        ("archives", "0011_remove_collectiongallery_name"),
        ("content", "0003_alter_inducteephotoplaceholder_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticleListPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wahf.mixins.OpenGraphMixin, "wagtailcore.page"),
        ),
        migrations.CreateModel(
            name="ArticlePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("date", models.DateField(blank=True, null=True)),
                (
                    "short_description",
                    models.TextField(
                        help_text="A short description of this gallery, used for gallery list page and social media preview."
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "heading",
                                wagtail.blocks.CharBlock(form_classname="title"),
                            ),
                            ("paragraph", wagtail.blocks.RichTextBlock()),
                            ("image", wagtail.images.blocks.ImageChooserBlock()),
                        ],
                        use_json_field=True,
                    ),
                ),
                (
                    "byline",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="archives.person",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Thumbnail and social media preview image for this gallery.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="archives.wahfimage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wahf.mixins.OpenGraphMixin, "wagtailcore.page"),
        ),
    ]
