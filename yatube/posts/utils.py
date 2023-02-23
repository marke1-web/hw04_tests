from django.core.paginator import Paginator

POST_COUNT_PER_PAGE = 10


def pagin(request, posts):
    paginator = Paginator(posts, POST_COUNT_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
