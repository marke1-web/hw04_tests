from django.urls import reverse
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username="TestAuth")
        cls.user_author = User.objects.create_user(username="TestAuthor")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Тестовый пост", author=cls.user_author, group=cls.group
        )
        """Шаблоны по адресам"""
        cls.templates_url_names = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.post.author.username}/": "posts/profile.html",
            f"/posts/{cls.post.pk}/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            f"/posts/{cls.post.pk}/edit/": "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user_auth)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user_author)

    def test_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина
        """
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_post_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /post/<int:post_id>/edit/> перенаправялет аноним
        пользователя на страницу логина
        """
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_post_post_edit_url_redirect_anonymous_on_auth_login(self):
        response = self.guest_client.get(
            f"/posts/{PostURLTests.post.pk}/edit/", follow=True
        )
        self.assertRedirects(
            response,
            (f"/auth/login/?next=/posts/{PostURLTests.post.pk}/edit/"),
        )

    def test_post_create_url_exists_at_desired_location_authorizied(self):
        """
        Проверка доступности страницы /create/ авторизованному
        пользователю
        """
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_authorizied_on_post_detail(self):
        """Страница по адресу /post/<int:post_id>/edit/ перенаправит авторизван
        пользователя на страницу поста
        """
        response = self.authorized_client.get(
            f"/posts/{PostURLTests.post.pk}/edit/", follow=True
        )
        self.assertRedirects(response, (f"/posts/{PostURLTests.post.pk}/"))

    def test_post_edit_url_exixts_at_desired_location_authorizied(self):
        """Проверка допустимости страницы /post/<int:post_id>/edit/ автору
        поста
        """
        response = self.author_client.get(
            f"/posts/{PostURLTests.post.pk}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверка использования URl адреса к шаблонам"""

        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_author_status_code(self):
        """Проверка автора"""
        status_code_url = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in status_code_url.items():
            with self.subTest(url=url):
                status_code = self.author_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_author_status_code(self):
        """Проверка авториз пользователя"""
        status_code_url = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in status_code_url.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_author_status_code(self):
        """Проверка  не авториз пользователя"""
        status_code_url = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'bad_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, response_code in status_code_url.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    class StaticURLTests(TestCase):
        def setUp(self):
            self.guest_client = Client()

        def test_homepage(self):
            responce = self.guest_client.get("/")
            self.assertEqual(responce.status_code, HTTPStatus.OK)
