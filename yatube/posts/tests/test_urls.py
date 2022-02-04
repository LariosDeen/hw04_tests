from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='MikeyMouse')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='mouses',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_public_pages(self):
        """Проверяем вход незарегистрированного пользователя
        на общедоступные страницы.
        """
        public_pages_list = [
            '/',
            '/group/mouses/',
            '/profile/MikeyMouse/',
            '/posts/1/',
        ]
        for page in public_pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_edit_page(self):
        """Проверяем доступность страниц для автора"""
        author_pages_list = [
            '/',
            '/group/mouses/',
            '/profile/MikeyMouse/',
            '/posts/1/',
            '/posts/1/edit/',
            '/create/',
        ]
        for page in author_pages_list:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        authorized_pages_list = [
            '/',
            '/group/mouses/',
            '/profile/MikeyMouse/',
            '/posts/1/',
            '/create/',
        ]
        user = User.objects.create_user(username='SpiderMan')
        authorized_client = Client()
        authorized_client.force_login(user)
        for page in authorized_pages_list:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Проверяем статус несуществующей страницы"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_templates(self):
        """Проверяем вызываемые шаблоны для соответствующих url"""
        url_template_list = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/group/mouses/': 'posts/group_list.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/profile/MikeyMouse/': 'posts/profile.html',
        }
        for url, template in url_template_list.items():
            with self.subTest(template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
