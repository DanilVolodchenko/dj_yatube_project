from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

from posts.models import User


USER_USERNAME = 'TestUser'

SIGNUP_URL = reverse('users:signup')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
PASSWORD_RESET_URL = reverse('users:password_reset')
PASSWORD_RESET_DONE_URL = reverse('users:password_reset_done')
PASSWORD_RESET_CONFIRM_URL = reverse('users:password_reset_confirm',
                                     kwargs={'uidb64': 'Mg', 'token':
                                             '684-a4dbc9428db7cae7e35'})
PASSWORD_RESET_COMPLETE_URL = reverse('users:password_reset_complete')
PASSWORD_CHANGE_URL = reverse('users:password_change')
PASSWORD_CHANGE_DONE_URL = reverse('users:password_change_done')

SIGNUP_TEMPLATE = 'users/signup.html'
LOGIN_TEMPLATE = 'users/login.html'
LOGOUT_TEMPLATE = 'users/logged_out.html'
PASSWORD_RESET_TEMPLATE = 'users/password_reset_form.html'
PASSWORD_RESET_DONE_TEMPLATE = 'users/password_reset_done.html'
PASSWORD_RESET_CONFIRM_TEMPLATE = 'users/password_reset_confirm.html'
PASSWORD_RESET_COMPLETE_TEMPLATE = 'users/password_reset_complete.html'
PASSWORD_CHANGE_TEMPLATE = 'users/password_change_form.html'
PASSWORD_CHANGE_DONE_TEMPLATE = 'users/password_change_done.html'


class PostURLTest(TestCase):
    def setUp(self):
        """Создает неавторизованного и авторизованного пользователей."""
        self.guest_client = Client()
        self.user = User.objects.create_user(USER_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_addresses_users_url_for_guest_client(self):
        """Страницы adresses доступные пользователям."""
        addresses = [
            SIGNUP_URL,
            LOGIN_URL,
            LOGOUT_URL,
            PASSWORD_RESET_URL,
            PASSWORD_RESET_DONE_URL,
            PASSWORD_RESET_CONFIRM_URL,
            PASSWORD_RESET_COMPLETE_URL,
            # PASSWORD_CHANGE_URL,
            # PASSWORD_CHANGE_DONE_URL,
        ]
        for address in addresses:
            with self.subTest(addresses=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_addresses_users_url_for_auth_client(self):
        """Страницы adresses доступные только авторизованному пользователю."""
        addresses = [
            SIGNUP_URL,
            LOGIN_URL,
            LOGOUT_URL,
            PASSWORD_RESET_URL,
            PASSWORD_RESET_DONE_URL,
            PASSWORD_RESET_CONFIRM_URL,
            PASSWORD_RESET_COMPLETE_URL,
            # PASSWORD_CHANGE_URL,
            # PASSWORD_CHANGE_DONE_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            SIGNUP_URL: SIGNUP_TEMPLATE,
            LOGIN_URL: LOGIN_TEMPLATE,
            LOGOUT_URL: LOGOUT_TEMPLATE,
            PASSWORD_RESET_URL: PASSWORD_RESET_TEMPLATE,
            PASSWORD_RESET_DONE_URL: PASSWORD_RESET_DONE_TEMPLATE,
            PASSWORD_RESET_COMPLETE_URL: PASSWORD_RESET_COMPLETE_TEMPLATE,
            PASSWORD_RESET_CONFIRM_URL: PASSWORD_RESET_CONFIRM_TEMPLATE,
            # PASSWORD_CHANGE_URL: PASSWORD_CHANGE_TEMPLATE,
            # PASSWORD_CHANGE_DONE_URL: PASSWORD_CHANGE_DONE_TEMPLATE
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
