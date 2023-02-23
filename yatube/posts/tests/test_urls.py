from django.core.cache import cache
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post, User

AUTHOR_USERNAME = 'TestAuthor'
USER_USERNAME = 'TestUser'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
POST_ID = 1

INDEX_URL = '/'
GROUP_LIST_URL = f'/group/{GROUP_SLUG}/'
PROFILE_URL = f'/profile/{AUTHOR_USERNAME}/'
POST_DETAIL_URL = f'/posts/{POST_ID}/'
POST_EDIT_URL = f'/posts/{POST_ID}/edit/'
CREATE_URL = '/create/'

INDEX_TEMPLATE = 'posts/index.html'
GROUP_LIST_TEMPLATE = 'posts/group_list.html'
PROFILE_TEMPLATE = 'posts/profile.html'
POST_DETAIL_TEMPLATE = 'posts/post_detail.html'
POST_CREATE_AND_EDIT_TEMPLATE = 'posts/create_post.html'


class PostURLTest(TestCase):
    user = None

    @classmethod
    def setUpClass(cls):
        """Создает БД."""
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            id=POST_ID,
            author=cls.user,
        )

    def setUp(self):
        """Создает неавторизованного и авторизованного пользователей."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        cache.clear()

    def test_addresses_url_for_guest_client(self):
        """Страницы adresses доступные всем пользователям."""
        addresses = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
            POST_DETAIL_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_addresses_url_for_auth_client(self):
        """Страница доступная только авторизованному пользователю."""
        response = self.authorized_client.get(CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_addresses_url_for_author(self):
        """Страница доступная только автору поста."""
        response = self.authorized_client.get(POST_EDIT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_address_not_exists_for_all_client(self):
        """Доступ к несуществующей страницы."""
        response = self.guest_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: INDEX_TEMPLATE,
            GROUP_LIST_URL: GROUP_LIST_TEMPLATE,
            PROFILE_URL: PROFILE_TEMPLATE,
            POST_DETAIL_URL: POST_DETAIL_TEMPLATE,
            POST_EDIT_URL: POST_CREATE_AND_EDIT_TEMPLATE,
            CREATE_URL: POST_CREATE_AND_EDIT_TEMPLATE,
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
