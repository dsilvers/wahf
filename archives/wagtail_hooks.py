from django.contrib.auth.decorators import login_required
from django.urls import re_path as url
from django.urls import reverse
from django.utils.decorators import method_decorator
from djqscsv import render_to_csv_response
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail_modeladmin.helpers import AdminURLHelper, ButtonHelper
from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.views import IndexView

from content.models import ArticleAuthor, FourtyYearsStory, ScholarshipRecipient
from users.models import Member

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


modeladmin_register(ScholarshipRecipientAdmin)
modeladmin_register(ArticleAuthorAdmin)
modeladmin_register(MemberTypeAdmin)
modeladmin_register(FourtyYearsStoryAdmin)
