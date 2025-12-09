from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from taggit.models import Tag

from content.models import ArticlePage, InducteeDetailPage, PageTag


def old_website_inductee_redirect(request, slug):
    inductee = InducteeDetailPage.objects.filter(last_name__iexact=slug).first()

    if inductee:
        return HttpResponsePermanentRedirect(inductee.full_url)
    else:
        raise Http404("Inductee not found")


class TagView(TemplateView):
    template_name = "content/tag_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        article_page_content_type = ContentType.objects.get_for_model(ArticlePage)
        inductee_page_content_type = ContentType.objects.get_for_model(
            InducteeDetailPage
        )

        tag = get_object_or_404(Tag, slug=kwargs.get("slug"))

        article_page_pks = PageTag.objects.filter(
            tag=tag, content_object__content_type=article_page_content_type
        ).values_list("content_object__pk", flat=True)[0:100]
        inductee_page_pks = PageTag.objects.filter(
            tag=tag, content_object__content_type=inductee_page_content_type
        ).values_list("content_object__pk", flat=True)[0:100]

        context["articles"] = ArticlePage.objects.filter(pk__in=article_page_pks)
        context["inductees"] = InducteeDetailPage.objects.filter(
            pk__in=inductee_page_pks
        )

        context["articles_found"] = context["articles"].exists()
        context["inductees_found"] = context["inductees"].exists()

        context["tag"] = tag

        context["page_title"] = f"Inductees and Articles - {tag.name}"

        return context
