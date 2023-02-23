from django.test import TestCase, Client

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

        """Статус коды"""
        cls.status_code_url_names = {
            "/": 200,
            f"/group/{cls.group.slug}/": 200,
            f"/profile/{cls.post.author.username}/": 200,
            f"/posts/{cls.post.pk}/": 200,
            "/unexisting_page/": 404,
        }

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

    def test_not_auth_url_exists_at_desired_location(self):
        """Проверка работы общедоступных страниц"""
        for address, status_code in self.status_code_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

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
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """Проверка использования URl адреса к шаблонам"""
        # templates_url_names = ()
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    class StaticURLTests(TestCase):
        def setUp(self):
            self.guest_client = Client()

        def test_homepage(self):
            responce = self.guest_client.get("/")
            self.assertEqual(responce.status_code, 200)
