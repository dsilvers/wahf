from django.conf import settings

# from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from users import views as user_views

urlpatterns = [
    # path("django-admin/", admin.site.urls),
    # WAGTAIL ADMIN
    path("cms/autocomplete/", include(autocomplete_admin_urls)),
    path("cms/", include(wagtailadmin_urls)),
    # WAGTAIL DOCUMENT VIEWER
    path("documents/", include(wagtaildocs_urls)),
    # MEMBERSHIP
    # ACCOUNT UPDATES
    path(
        "membership/join", user_views.MemberJoinView.as_view(), name="membership_join"
    ),
    path(
        "account/member-profile",
        user_views.MemberProfileView.as_view(),
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
    # PAYMENT PROCESSING
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
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
