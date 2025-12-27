import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.urls import re_path as url
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from djqscsv import render_to_csv_response
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.documents import get_document_model
from wagtail_modeladmin.helpers import AdminURLHelper, ButtonHelper
from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.views import IndexView

from content.filters import InducteeDetailPageFilterSet
from content.models import (
    ArticleAuthor,
    FourtyYearsStory,
    InducteeDetailPage,
    LocationTag,
    ScholarshipRecipient,
)
from membership.models import Member

Document = get_document_model()


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


# https://parbhatpuri.com/add-download-csv-option-in-wagtail-modeladmin.html
# https://tkainrad.dev/posts/export-wagtail-modeladmin-tables-to-csv/


class ExportButtonHelper(ButtonHelper):
    export_button_classnames = ["icon", "icon-download"]

    def export_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []

        classnames = self.export_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        text = "Export {} to CSV".format(self.verbose_name_plural.title())

        return {
            "url": self.url_helper.get_action_url(
                "export", query_params=self.request.GET
            ),
            "label": text,
            "classname": cn,
            "title": text,
        }


class ExportAdminURLHelper(AdminURLHelper):
    non_object_specific_actions = ("create", "choose_parent", "index", "export")

    def get_action_url(self, action, *args, **kwargs):
        query_params = kwargs.pop("query_params", None)

        url_name = self.get_action_url_name(action)
        if action in self.non_object_specific_actions:
            url = reverse(url_name)
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)

        if query_params:
            url += "?{params}".format(params=query_params.urlencode())

        return url

    def get_action_url_pattern(self, action):
        if action in self.non_object_specific_actions:
            return self._get_action_url_pattern(action)

        return self._get_object_specific_action_url_pattern(action)


class ExportView(IndexView):
    model_admin = None

    def export_csv(self):
        if (self.model_admin is None) or not hasattr(
            self.model_admin, "csv_export_fields"
        ):
            data = self.queryset.all().values()
        else:
            data = self.queryset.all().values(*self.model_admin.csv_export_fields)
        return render_to_csv_response(data)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        return self.export_csv()


class ExportModelAdminMixin(object):
    button_helper_class = ExportButtonHelper
    url_helper_class = ExportAdminURLHelper
    export_view_class = ExportView

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            url(
                self.url_helper.get_action_url_pattern("export"),
                self.export_view,
                name=self.url_helper.get_action_url_name("export"),
            ),
        )
        return urls

    def export_view(self, request):
        kwargs = {"model_admin": self}
        view_class = self.export_view_class
        return view_class.as_view(**kwargs)(request)


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


class FourtyYearsStoryAdmin(ThumbnailMixin, ModelAdmin):
    model = FourtyYearsStory
    base_url_path = "fourtyyears"  # customise the URL from default to admin/bookadmin
    menu_item_name = "40th"
    menu_icon = "pick"  # change as required
    menu_order = 214  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    thumb_image_field_name = "image"
    list_display = (
        "short_title",
        "article_number",
        "admin_thumb",
    )


class LocationTagAdmin(ModelAdmin):
    model = LocationTag
    base_url_path = "locations"  # customise the URL from default to admin/bookadmin
    menu_icon = "globe"  # change as required
    menu_order = 202  # will put in 3rd place (000 being 1st, 100 2nd)
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )

    list_display = (
        "get_display_name",
        "name",
        "slug",
        "location_name",
        "latitude",
        "longitude",
    )


class MemberTypeAdmin(ExportModelAdminMixin, ThumbnailMixin, ModelAdmin):
    index_template_name = "wagtailadmin/export_csv.html"
    model = Member
    base_url_path = "memberadmin"  # customise the URL from default to admin/bookadmin
    menu_icon = "group"  # change as required
    menu_order = 199  # will put in 3rd place (000 being 1st, 100 2nd)
    # add_to_settings_menu = True  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    # add_to_admin_menu = False  # or False to exclude your model from the menu
    # https://stackoverflow.com/questions/73200676/is-there-a-way-to-show-images-in-a-wagtail-model-admin-record-listing-page
    # thumb_image_field_name = "image"
    list_display = (
        "email",
        "first_name",
        "last_name",
        "membership_level",
        "membership_expiry_date",
    )
    list_filter = ("membership_level", "stripe_subscription_active")
    search_fields = ("email", "first_name", "last_name", "spouse_name", "business_name")

    csv_export_fields = [
        "pk",
        "user__pk",
        "email",
        "first_name",
        "last_name",
        "spouse_name",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "zip",
        "phone",
        "membership_level__name",
        "membership_join_date",
        "last_payment_date",
        "membership_expiry_date",
        "stripe_customer_id",
        "stripe_subscription_id",
        "stripe_subscription_active",
    ]

    panels = [
        FieldPanel("email"),
        FieldPanel("first_name"),
    ]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("first_name"),
                FieldPanel("last_name"),
                FieldPanel("spouse_name"),
                FieldPanel("business_name"),
            ],
            heading="Member Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("address_line1"),
                FieldPanel("address_line2"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("zip"),
                FieldPanel("phone"),
            ],
            heading="Member Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("membership_level"),
                FieldPanel("membership_join_date"),
                FieldPanel("last_payment_date"),
                FieldPanel("membership_expiry_date"),
            ],
            heading="Membership Level and Payments",
        ),
        MultiFieldPanel(
            [
                FieldPanel("stripe_subscription_active"),
                FieldPanel("stripe_customer_id"),
                FieldPanel("stripe_subscription_id"),
            ],
            heading="Stripe Settings",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_download_stats_menu_item():
    """Adds a 'Download Stats' link to the main Wagtail sidebar menu, restricted to Superusers."""
    return MenuItem(
        "Download Stats",
        reverse("download_stats"),
        icon_name="download",
        order=1000,
    )


class InducteeDetailPageListingViewSet(PageListingViewSet):
    # The model this viewset manages
    model = InducteeDetailPage

    # Configuration for the admin menu
    icon = "tags"  # Use an appropriate icon
    menu_label = "Inductee Locations Audit"
    add_to_admin_menu = True  # Adds a new item to the main sidebar menu

    # Crucially, assign your custom filterset class
    filterset_class = InducteeDetailPageFilterSet

    # Define which columns appear in the list view (optional, but good practice)
    list_display = (
        "admin_display_title",
        "live",
        "first_published_at",
        "latest_revision_created_at",
    )


# Register the viewset with Wagtail
@hooks.register("register_admin_viewset")
def register_inductee_detail_page_tag_audit_listing_viewset():
    # The first argument must be a unique name
    return InducteeDetailPageListingViewSet("inductee_detail_page_audit_listing")


@hooks.register("register_rich_text_features")
def register_highlight_feature(features):
    feature_name = "highlight"
    type_ = "HIGHLIGHT"
    tag = "mark"

    control = {
        "type": type_,
        "icon": "pick",
        "description": "Highlight",
        # This helps group it with other inline styles like Bold/Italic
        "group": "blocks",
    }

    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: tag}},
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)
    features.default_features.append(feature_name)


# This isn't working
@hooks.register("insert_global_admin_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("css/wagtail-editor.css")
    )


modeladmin_register(LocationTagAdmin)
modeladmin_register(ScholarshipRecipientAdmin)
modeladmin_register(ArticleAuthorAdmin)
modeladmin_register(MemberTypeAdmin)
modeladmin_register(FourtyYearsStoryAdmin)
