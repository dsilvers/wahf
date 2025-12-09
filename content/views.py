from django.http import Http404, HttpResponsePermanentRedirect

from content.models import InducteeDetailPage


def old_website_inductee_redirect(request, slug):
    inductee = InducteeDetailPage.objects.filter(last_name__iexact=slug).first()

    if inductee:
        return HttpResponsePermanentRedirect(inductee.full_url)
    else:
        raise Http404("Inductee not found")
