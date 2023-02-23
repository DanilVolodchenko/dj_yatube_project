from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


AUTHOR_URL = reverse('about:author')
TECH_URL = reverse('about:tech')

AUTHOR_TEMPLATE = 'about/author.html'
TECH_TEMPLATE = 'about/tech.html'


class PostURLTest(TestCase):

    def setUp(self):
        """Создает неавторизованного пользователея."""
        self.guest_client = Client()

    def test_addresses_url_for_clients(self):
        """Проверяет траницы addresses для любого пользователя"""
        addresses = [
            AUTHOR_URL,
            TECH_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                responce = self.guest_client.get(address)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            AUTHOR_URL: AUTHOR_TEMPLATE,
            TECH_URL: TECH_TEMPLATE,
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
