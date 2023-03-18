from wagtail import hooks
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import User


class MembershipAdmin(ModelAdmin):
    model = User
    base_url_path = (
        "membershipadmin"  # customise the URL from default to admin/bookadmin
    )
    menu_label = "Members"
    menu_icon = "user"  # change as required
    menu_order = 90  # will put in 3rd place (000 being 1st, 100 2nd)
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


modeladmin_register(MembershipAdmin)


@hooks.register("construct_main_menu")
def reorder_menu_items(request, menu_items):
    for item in menu_items:
        match item.name:
            # members 90
            # explorer 100
            case "images":
                item.order = 110
            case "documents":
                item.order = 120
            # people 130
            case "snippets":
                item.order = 140
            case "_":
                pass
        # print(item.name, item.order)
        # if item.name == 'explorer':  # internal name for the Pages menu item
        #    item.order = 100000
        #    break
