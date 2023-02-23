from django.test import TestCase


class CoreTest(TestCase):

    def test_404_use_correct_templates(self):
        """Проверяет шаблон страницы 404"""
        response = self.client.get('/unexists/')
        self.assertTemplateUsed(response, 'core/404.html')
