import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Comment
from posts.tests.constants import (
    AUTHOR_USERNAME,
    USER_USERNAME,
    POST_ID,
    POST_TEXT,
    POST_NEW_TEXT,
    GROUP_ID,
    GROUP_TITLE,
    GROUP_SLUG,
    NEW_GROUP_ID,
    NEW_GROUP_TITLE,
    NEW_GROUP_SLUG,
    GROUP_DESCRIPTION,
    COMMENT_ID,
    COMMENT_TEXT,
    COMMENT_EDIT_TEXT,
)

IMAGE_NAME = 'test_image.gif'
TYPE_OF_IMAGE = 'image/gif'
NEW_IMAGE_NAME = 'test_image_new.gif'

PROFILE_URL = reverse('posts:profile', kwargs={'username': AUTHOR_USERNAME})
POST_DETAIL_URL = reverse('posts:post_detail', kwargs={'post_id': POST_ID})
POST_EDIT_URL = reverse('posts:post_edit', kwargs={'post_id': POST_ID})
CREATE_URL = reverse('posts:post_create')
COMMENT_EDIT_URL = reverse('posts:edit_comment',
                           kwargs={'post_id': POST_ID,
                                   'comment_id': COMMENT_ID})
COMMENT_DELETE_URL = reverse('posts:delete_comment',
                             kwargs={'post_id': POST_ID,
                                     'comment_id': COMMENT_ID})
LOGIN_URL = reverse('users:login')
POST_CREATE_URL = reverse('posts:post_create')
POST_DELETE_URL = reverse('posts:post_delete', kwargs={'post_id': POST_ID})
ADD_COMMENT = reverse('posts:add_comment', kwargs={'post_id': POST_ID})
TEST_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name=IMAGE_NAME,
    content=TEST_GIF,
    content_type=TYPE_OF_IMAGE
)
TEST_GIF_NEW = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED_NEW = SimpleUploadedFile(
    name=NEW_IMAGE_NAME,
    content=TEST_GIF_NEW,
    content_type=TYPE_OF_IMAGE
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    user = None
    group = None

    @classmethod
    def setUpClass(cls):
        """Создает БД."""
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            id=GROUP_ID,
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.user = User.objects.create_user(username=USER_USERNAME)

    @classmethod
    def tearDownClass(cls):
        """Удаляет папку с картинкой."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создает пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
                author=self.author,
                group=self.group.id,
                image=f'posts/{IMAGE_NAME}'
            ).exists()
        )

    def test_author_can_change_post_edit(self):
        """Изменение поста с post_id."""
        Post.objects.create(
            id=POST_ID,
            text=POST_TEXT,
            group=self.group,
            author=self.author,
        )
        new_group = Group.objects.create(
            id=NEW_GROUP_ID,
            title=NEW_GROUP_TITLE,
            slug=NEW_GROUP_SLUG
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_NEW_TEXT,
            'group': new_group.id,
            'image': UPLOADED_NEW
        }
        response = self.authorized_client.post(
            POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, POST_DETAIL_URL)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=POST_NEW_TEXT,
                author=self.author,
                group=new_group.id,
                image=f'posts/{NEW_IMAGE_NAME}'
            ).exists()
        )

    def test_guest_client_can_not_create_post(self):
        """Проверяет создание поста неавторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': UPLOADED_NEW,
        }
        response = self.client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        redirect_url = (LOGIN_URL
                        + '?next='
                        + POST_CREATE_URL)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=POST_TEXT,
                author=self.author,
                group=self.group.id,
            ).exists()
        )

    def test_comment_authorized_client(self):
        """Комментировать посты может только авторизованный пользователь
        и комментарий появляется на странице."""
        comments_count = Comment.objects.count()
        Post.objects.create(
            id=POST_ID,
            text=POST_TEXT,
            author=self.author,
        )
        form_data = {
            'text': COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=COMMENT_TEXT,
                author=self.author,
            ).exists()
        )

    def test_post_author_delete(self):
        """Удаление поста автором"""
        Post.objects.create(
            id=POST_ID,
            text=POST_TEXT,
            author=self.author,
        )
        post_cnt = Post.objects.count()
        response = self.authorized_client.post(
            POST_DELETE_URL,
            follow=True,
        )
        self.assertNotEqual(Post.objects.count(), post_cnt)
        self.assertRedirects(response, PROFILE_URL)
        self.assertFalse(
            Post.objects.filter(
                text=POST_TEXT,
                author=self.author
            ).exists()
        )

    def test_comment_author_edit(self):
        """Изменение комментария автором комментария"""
        post = Post.objects.create(
            text=POST_TEXT,
            author=self.user
        )
        Comment.objects.create(
            pk=COMMENT_ID,
            post=post,
            text=COMMENT_TEXT,
            author=self.author,
        )
        comment_cnt = Comment.objects.count()
        form_data = {
            'text': COMMENT_EDIT_TEXT
        }
        response = self.authorized_client.post(
            COMMENT_EDIT_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comment_cnt)
        self.assertTrue(
            Comment.objects.filter(
                text=COMMENT_EDIT_TEXT,
                author=self.author
            ).exists()
        )

    def test_comment_author_delete(self):
        """Удаление комментария автором комментария"""
        post = Post.objects.create(
            text=POST_TEXT,
            author=self.user
        )
        Comment.objects.create(
            pk=COMMENT_ID,
            post=post,
            text=COMMENT_TEXT,
            author=self.author,
        )
        comment_cnt = Comment.objects.count()
        print(comment_cnt)
        response = self.authorized_client.post(
            COMMENT_DELETE_URL,
            follow=True
        )
        self.assertNotEqual(Comment.objects.count(), comment_cnt)
        self.assertRedirects(response, POST_DETAIL_URL)
        self.assertFalse(
            Comment.objects.filter(
                text=COMMENT_TEXT,
                author=self.author
            ).exists()
        )
