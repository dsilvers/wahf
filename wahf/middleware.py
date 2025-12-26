from wagtail.models import Page, Site


class AdminDraftPreviewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only proceed if we got a 404 and the user is staff
        if (
            response.status_code == 404
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        ):
            site = Site.find_for_request(request)
            if not site:
                return response

            path = request.path
            if not path.endswith("/"):
                path += "/"

            full_url_path = f"{site.root_page.url_path}{path.lstrip('/')}"

            try:
                # Find the specific version of the page (to get your custom fields)
                page = Page.objects.get(url_path=full_url_path).specific

                if not page.live:
                    # Trigger the page's serve method
                    preview_response = page.serve(request)

                    if hasattr(preview_response, "render") and callable(
                        preview_response.render
                    ):
                        preview_response.render()

                    return preview_response
            except (Page.DoesNotExist, Page.MultipleObjectsReturned):
                pass

        return response
