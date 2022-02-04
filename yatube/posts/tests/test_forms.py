import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='MikeyMouse')
        cls.group = Group.objects.create(
            title='Тестовая группа mouses',
            slug='mouses',
            description='Описание тестовой группы mouses',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            pub_date='01.02.2022',
            group_id=cls.group.id
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_create_post_saved(self):
        """При отправке валидной формы со страницы create
        создаётся новая запись в базе данных
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст вновь созданного поста',
            'group': self.group.id,
            'author': self.user
        }
        self.author_client.post(
            '/create/',
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_changed(self):
        """При отправке валидной формы со страницы post_edit
        происходит изменение поста с отправленным id в базе данных
        """
        form_data = {
            'text': 'Текст изменённого поста',
            'group': self.group.id,
        }
        self.author_client.post(
            f'/posts/{self.post.id}/edit/',
            data=form_data,
            follow=True,
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(changed_post.text, form_data['text'])
