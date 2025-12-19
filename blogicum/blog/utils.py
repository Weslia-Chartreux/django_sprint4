from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.constants import DEFAULT_NUM_PAGE, POSTS_ON_PAGE
from blog.models import Post


def posts_pagination(request, posts):
    page_number = request.GET.get(
        'page',
        DEFAULT_NUM_PAGE
    )
    paginator = Paginator(posts, POSTS_ON_PAGE)
    return paginator.get_page(page_number)


def query_post(
        manager=Post.objects,
        filters=True,
        with_comments=True
):
    queryset = manager.select_related('author', 'location', 'category')
    if filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )
    if with_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))
    return queryset.order_by('-pub_date')
