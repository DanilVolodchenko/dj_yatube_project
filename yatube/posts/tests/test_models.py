from django.test import TestCase

from posts.models import Post, Group, User

AUTHOR_USERNAME = 'TestAuthor'
GROUP_TITLE = 'Тестовая группа'
POST_TEXT = 'Тестовый текст'

NUMBER_OF_SYMBOLS = 15


class PostModelTest(TestCase):
    author = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:NUMBER_OF_SYMBOLS], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
