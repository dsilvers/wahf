from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from content.models import ArticleAuthor, ScholarshipRecipient

from .models import AircraftType, Location, Person


class ScholarshipRecipientAdmin(ThumbnailMixin, ModelAdmin):
    model = ScholarshipRecipient
    base_url_path = (
        "scholarshipadmin"  # customise the URL from default to admin/bookadmin
    )
    menu_icon = "pick"  # change as required
    menu_order = 204  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    thumb_image_field_name = "image"
    list_display = (
        "recipient_name",
        "scholarship_name",
        "year",
        "admin_thumb",
    )
    # list_filter = ('name', )
    # search_fields = ('name', )


class ArticleAuthorAdmin(ThumbnailMixin, ModelAdmin):
    model = ArticleAuthor
    base_url_path = "articleauthor"  # customise the URL from default to admin/bookadmin
    menu_icon = "pick"  # change as required
    menu_order = 212  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    thumb_image_field_name = "image"
    list_display = (
        "name",
        "admin_thumb",
    )
    # list_filter = ('name', )
    # search_fields = ('name', )


class PersonAdmin(ThumbnailMixin, ModelAdmin):
    model = Person
    base_url_path = "personadmin"  # customise the URL from default to admin/bookadmin
    menu_icon = "pick"  # change as required
    menu_order = 202  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    thumb_image_field_name = "image"
    list_display = (
        "name",
        "admin_thumb",
    )
    # list_filter = ('name', )
    # search_fields = ('name', )


class LocationAdmin(ThumbnailMixin, ModelAdmin):
    model = Location
    base_url_path = "locationadmin"  # customise the URL from default to admin/bookadmin
    menu_icon = "globe"  # change as required
    menu_order = 201  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    # thumb_image_field_name = "image"
    list_display = (
        "name",
        # "admin_thumb",
    )
    # list_filter = ('name', )
    # search_fields = ('name', )


class AircraftTypeAdmin(ThumbnailMixin, ModelAdmin):
    model = AircraftType
    base_url_path = (
        "aircrafttypeadmin"  # customise the URL from default to admin/bookadmin
    )
    menu_icon = "tag"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    # thumb_image_field_name = "image"
    list_display = (
        "name",
        # "admin_thumb",
    )
    # list_filter = ('name', )
    # search_fields = ('name', )


modeladmin_register(PersonAdmin)
modeladmin_register(LocationAdmin)
modeladmin_register(AircraftTypeAdmin)
modeladmin_register(ScholarshipRecipientAdmin)
modeladmin_register(ArticleAuthorAdmin)
