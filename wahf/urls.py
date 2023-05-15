from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from content import views as content_views
from membership import views as membership_views
from membership import webhooks as membership_webhook_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    # WAGTAIL ADMIN
    path("cms/autocomplete/", include(autocomplete_admin_urls)),
    path("cms/", include(wagtailadmin_urls)),
    # WAGTAIL DOCUMENT VIEWER
    path("documents/", include(wagtaildocs_urls)),
    # MEMBERSHIP
    # ACCOUNT UPDATES
    path(
        "membership/", membership_views.MemberJoinView.as_view(), name="membership-join"
    ),
    path(
        "membership/payment/",
        membership_views.MemberJoinPaymentView.as_view(),
        name="membership-join-payment",
    ),
    path(
        "membership/thanks/",
        membership_views.MemberJoinThanks.as_view(),
        name="membership-join-thanks",
    ),
    path("stripe-webhooks/", membership_webhook_views.process_stripe_webhook),
    path(
        "account/member-profile",
        membership_views.MemberProfileView.as_view(),
        name="member_profile",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    # SEARCH ENGINE STUFF
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots.txt",
    ),
    path("sitemap.xml", sitemap),
    # OLD WEBSITE REDIRECTS
    path(
        "inductees/<slug:slug>.htm",
        content_views.old_website_inductee_redirect,
        name="old_inductee_redirect",
    ),
]


if settings.DEBUG:
    from django.conf.urls.static import static  # noqa
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = urlpatterns + [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
]
