from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from http import HTTPStatus
from django.core.cache import cache

from posts.models import Group, Post, User
from posts.tests.constants import (
    AUTHOR_USERNAME,
    USER_USERNAME,
    POST_ID,
    POST_TEXT,
    NEW_POST_ID,
    POST_NEW_TEXT,
    GROUP_ID,
    GROUP_TITLE,
    GROUP_SLUG,
    GROUP_DESCRIPTION,
)

POST_PER_PAGE = 10
NUMBER_OF_POSTS = 2

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': GROUP_SLUG})
AUTHOR_PROFILE_URL = reverse('posts:profile',
                             kwargs={'username': AUTHOR_USERNAME})
USER_PROFILE_URL = reverse('posts:profile', kwargs={'username': USER_USERNAME})
POST_DETAIL_URL = reverse('posts:post_detail', kwargs={'post_id': POST_ID})
POST_EDIT_URL = reverse('posts:post_edit', kwargs={'post_id': POST_ID})
CREATE_URL = reverse('posts:post_create')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow',
                             kwargs={'username': AUTHOR_USERNAME})
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow',
                               kwargs={'username': AUTHOR_USERNAME})


class PostViewTest(TestCase):
    author = None
    group = None
    user = None

    @classmethod
    def setUpClass(cls):
        """Создает БД."""
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            id=GROUP_ID,
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

        cls.post = Post.objects.create(
            id=POST_ID,
            text=POST_TEXT,
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        """Создает неавторизованного и авторизованного пользователей."""
        self.guest_client = Client()
        self.user = User.objects.create_user(USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_urls_correct_context(self):
        """Проверяет index на правильный контекст."""
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(
            response.context['page_obj'][0], Post.objects.all()[0])

    def test_profile_correct_context(self):
        """Проверяет profile на правильный контекст."""
        response = self.guest_client.get(AUTHOR_PROFILE_URL)
        self.assertEqual(response.context['page_obj'][0], Post.objects.filter(
            author=self.post.author)[0])

    def test_post_detail_correct_context(self):
        """Проверяет post_detail на правильный контекст."""
        response = self.guest_client.get(POST_DETAIL_URL)
        self.assertEqual(
            response.context['post'], Post.objects.filter(id=self.post.id)[0])

    def test_post_with_group_in_URLs(self):
        """Проверяет, что пост с группой находится на страницах URL_LIST."""
        addresses = (INDEX_URL, GROUP_LIST_URL, AUTHOR_PROFILE_URL)
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if self.post.group:
                    self.assertIn(self.post, response.context['page_obj'])

    def test_post_not_in_mistake_group(self):
        """Проверяет, что пост не попал в другую группу."""
        response = self.guest_client.get(GROUP_LIST_URL)
        expected = Post.objects.exclude(group=self.post.group)
        self.assertNotIn(response.context['page_obj'], expected)

    def test_get_image_on_page(self):
        """Проверяет, что в контексте есть image."""
        addresses = [
            INDEX_URL,
            AUTHOR_PROFILE_URL,
            GROUP_LIST_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertIsNotNone(response.context['page_obj'][0].image)

        response = self.client.get(POST_DETAIL_URL)
        self.assertIsNotNone(response.context['post'].image)

    def test_follow_and_unfollow_authorized_client(self):
        """Подписка и отписка на автора."""
        response = self.authorized_client.get(
            PROFILE_FOLLOW_URL
        )
        self.assertRedirects(response, FOLLOW_INDEX_URL)

        response = self.authorized_client.get(
            PROFILE_UNFOLLOW_URL
        )
        self.assertRedirects(
            response,
            USER_PROFILE_URL
        )

    def test_context_create_on_follower(self):
        """Проверяет, что при добавлении поста автором,
        этот пост появляется у подписавшегося."""
        posts_cnt_before = Post.objects.filter(
            author__following__user=self.user).count()

        self.authorized_client.get(
            PROFILE_FOLLOW_URL
        )
        Post.objects.create(
            text=POST_NEW_TEXT,
            author=self.author
        )
        posts_cnt_after = Post.objects.filter(
            author__following__user=self.user).count()
        self.assertNotEqual(posts_cnt_before, posts_cnt_after)


class PaginatorViewsTest(TestCase):
    """Количество записей на странице."""

    NUMBER_OF_POSTS = 12
    group = None
    user = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        for post_num in range(cls.NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'{POST_TEXT} {post_num}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        cache.clear()

    def test_paginator_correct(self):
        """Тестирование пагинатора."""
        addresses = [
            INDEX_URL,
            GROUP_LIST_URL,
            AUTHOR_PROFILE_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response_1 = self.client.get(address)
                self.assertEqual(
                    len(response_1.context['page_obj']), POST_PER_PAGE)
                self.assertEqual(response_1.status_code, HTTPStatus.OK)
                response_2 = self.client.get(address + '?page=2')
                self.assertEqual(
                    len(response_2.context['page_obj']),
                    self.NUMBER_OF_POSTS - POST_PER_PAGE)
                self.assertEqual(response_2.status_code, HTTPStatus.OK)


class CacheViewsTest(TestCase):
    author = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(USER_USERNAME)
        cls.post_1 = Post.objects.create(
            id=POST_ID,
            text=POST_TEXT,
            author=cls.author,
        )
        cls.post_2 = Post.objects.create(
            id=NEW_POST_ID,
            text=POST_NEW_TEXT,
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_index_cache(self):
        """Проверяет кэш главной страницы."""
        # делаю первый запрос на страницу
        response_1 = self.authorized_client.get(INDEX_URL)
        # удаляю пост
        self.post_1.delete()
        # делаю второй запрос
        response_2 = self.authorized_client.get(INDEX_URL)
        # из-за кэша, количество постов не изменилось
        # очищаю кэш и делаю повторный запрос
        cache.clear()
        response_3 = self.authorized_client.get(INDEX_URL)
        self.assertEqual(response_1.content.decode('utf-8'),
                         response_2.content.decode('utf-8'))
        self.assertNotEqual(response_1.content.decode('utf-8'),
                            response_3.content.decode('utf-8'))
