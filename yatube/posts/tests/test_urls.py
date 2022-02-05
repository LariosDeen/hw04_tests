from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='MikeyMouse')
        cls.user_2 = User.objects.create_user(username='SpiderMan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='mouses',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_2,
            text='Тестовый пост',
        )
        cls.pages_list = [
            '/',
            '/group/mouses/',
            '/profile/MikeyMouse/',
            '/posts/1/',
            '/create/',
            '/posts/1/edit/',
        ]
        cls.url_template_dict = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/group/mouses/': 'posts/group_list.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/profile/MikeyMouse/': 'posts/profile.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_public_pages(self):
        """Проверяем вход незарегистрированного пользователя
        на общедоступные страницы.
        """
        for page in self.pages_list[:4]:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_redirect_pages(self):
        """Проверяем редирект незарегистрированного пользователя
        при попытке войти на страницы для зарегистрированного ползователя.
        """
        for page in self.pages_list[4:]:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 302)

    def test_edit_page(self):
        """Проверяем доступность страниц для автора."""
        for page in self.pages_list:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        """Проверяем доступность страниц для авторизованного пользователя."""
        for page in self.pages_list[:5]:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_redirect_for_authorized_client(self):
        """Проверяем редирект авторизованного пользователя при попытке
        войти на страницу редактирования поста для другого автора.
        """
        response = self.author_client.get('/posts/2/edit/')
        self.assertEqual(response.status_code, 302)

    def test_unexisting_page(self):
        """Проверяем статус несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_templates(self):
        """Проверяем вызываемые шаблоны для соответствующих URLs."""
        for url, template in self.url_template_dict.items():
            with self.subTest(template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
