from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Group, Post, User, Follow, Comment, Like
from .forms import PostForm, CommentForm
from .services import get_page

CACHE_TIME = 20


@cache_page(CACHE_TIME, key_prefix='index_page')
def index(request):
    """Выводит на страницу все посты авторов."""
    posts = Post.objects.all().select_related('author', 'group')
    page_obj = get_page(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводит на страницу посты определенной группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_page(request, posts)
    context = {
        'posts': posts,
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображает все посты определенного автора."""
    author = get_object_or_404(User.objects.prefetch_related(
        'posts', 'posts__group'), username=username)
    posts = author.posts.all()
    page_obj = get_page(request, posts)

    is_following = (request.user.is_authenticated
                    and author.following.filter(user=request.user).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'is_following': is_following,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отображает определенный пост автора по post_id."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    comments = post.comments.all()
    form = CommentForm()
    appraise_cnt = Like.objects.filter(post_id=post_id).count()
    is_like = post.like.filter(user=request.user).exists()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'appraise_cnt': appraise_cnt,
        'is_like': is_like
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создает пост автора."""
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('posts:profile', request.user)

        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирует запись поста автора."""
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=post,
        )

        if form.is_valid():
            # если данные изменились, сохраняет их
            if form.has_changed():
                form.save()

            return redirect('posts:post_detail', post_id)

        context = {'form': form, 'actions': 'edit'}
        return render(request, 'posts/create_post.html', context)

    form = PostForm(instance=post)
    context = {'form': form, 'actions': 'edit'}
    return render(request, 'posts/create_post.html', context)


@login_required()
def post_delete(request, post_id):
    """Автор удаляет свой пост"""
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html',
                  {'post': post, 'actions': 'delete'})


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к посту"""
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        form = CommentForm(
            request.POST,
            instance=comment
        )
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('posts:post_detail', post_id)
        context = {'form': form, 'actions': 'edit'}
        return render(request, 'posts/create_comment.html', context)

    form = CommentForm(instance=comment)
    context = {'form': form, 'actions': 'edit'}
    return render(request, 'posts/create_comment.html', context)


@login_required()
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_comment.html',
                  {'comment': comment, 'actions': 'delete'})


@login_required
def follow_index(request):
    """Выводит посты автора, на которые подписан пользователь."""
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    page_obj = get_page(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)

        return redirect('posts:follow_index')
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author)
    follow.delete()

    return redirect('posts:profile', user)


def post_like(request, post_id):
    """Понравился пост"""
    post = get_object_or_404(Post, pk=post_id)
    Like.objects.get_or_create(user=request.user, post=post)
    return redirect('posts:post_detail', post_id)


def post_dislike(request, post_id):
    """Понравился пост"""
    post = get_object_or_404(Post, pk=post_id)
    like = Like.objects.filter(user=request.user, post=post)
    like.delete()
    return redirect('posts:post_detail', post_id)


def search(request):
    """Производит поиск по посту"""
    # получаю текст, который ввел пользователь
    query = request.GET.get('query')
    if query.strip() != '':
        object_list = Post.objects.filter(
            Q(text__icontains=query) | Q(author__username__icontains=query)
        )
        return render(request,
                      'posts/search_result.html',
                      {'object_list': object_list})
    return redirect('posts:index')
