from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Person


class PersonAdmin(ThumbnailMixin, ModelAdmin):
    model = Person
    base_url_path = "personadmin"  # customise the URL from default to admin/bookadmin
    menu_icon = "user"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
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


modeladmin_register(PersonAdmin)
