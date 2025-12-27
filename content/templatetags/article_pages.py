from django import template

from ..models import ArticlePage

register = template.Library()


@register.inclusion_tag("content/article_list_objects.html")
def related_articles(page):
    related_pages = [
        related_page.link_to
        for related_page in page.related_articles.filter(page__live=True).all()
    ]
    exclude_pks = [article.pk for article in related_pages] + [page.pk]

    if len(related_pages) < 6:
        other_pages = (
            ArticlePage.objects.live()
            .exclude(pk__in=exclude_pks)
            .order_by("-website_publish_date", "-pk")[0:6]
        )
        for other_page in other_pages:
            related_pages.append(other_page)
            if len(related_pages) >= 6:
                break

    return {
        "articles_list": related_pages,
        "col_classes": "col-lg-4 col-md-6 col-sm-12",
        "article_class": "article-small",
    }
