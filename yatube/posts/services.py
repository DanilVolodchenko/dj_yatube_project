from django.core.paginator import Paginator

POSTS_PER_PAGE = 10


def get_page(request, post_list):
    """Пагинатор разделяет посты страницы на POSTS_PER_PAGE."""
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
