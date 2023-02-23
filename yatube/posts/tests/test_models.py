from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='Слаг группы',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        post_text = post.text
        self.assertEqual(str(post), post_text)

    def test_models_have_correct_group_title(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)
