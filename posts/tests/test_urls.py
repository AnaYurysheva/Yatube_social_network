from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test',
            slug='test-group',
            description='test1',)
        cls.user_edit = User.objects.create_user(username='AnnaY')
        cls.post = Post.objects.create(text='Tododo', author=cls.user_edit,)
        cls.authorized_client_edit = Client()
        cls.authorized_client_edit.force_login(cls.user_edit)

    def setUp(self):
        self.guest_client = Client()
        self.user_no_edit = User.objects.create_user(username='SashaS')
        self.authorized_client_no_edit = Client()
        self.authorized_client_no_edit.force_login(self.user_no_edit)

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        response = self.authorized_client_no_edit.get('/group/test-group/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_creation_url_redirect_anonymous(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_creation_url_exists_at_desired_location(self):
        response = self.authorized_client_no_edit.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        response = self.authorized_client_no_edit.get('/AnnaY/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_url_exists_at_desired_location(self):
        response = self.authorized_client_no_edit.get('/AnnaY/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_exists_at_desired_location(self):
        response = self.authorized_client_edit.get('/AnnaY/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_redirect_no_author(self):
        response = self.authorized_client_no_edit.get('/AnnaY/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_404_page_not_found(self):
        response = self.authorized_client_no_edit.get('/missing/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_id_edit_url_redirect_anonymous(self):
        response = self.guest_client.get('/AnnaY/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_url_redirect_anonymous(self):
        response = self.guest_client.get('/AnnaY/1/comment')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_url_exists_at_desired_location(self):
        response = self.authorized_client_no_edit.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-group/',
            'profile.html': '/AnnaY/',
            'post.html': '/AnnaY/1/',
            'new_post.html': '/AnnaY/1/edit/',
            'include/comments.html': '/AnnaY/1/',
            'follow.html': '/follow/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_edit.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_new_uses_correct_template(self):
        response = self.authorized_client_edit.get('/new/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_cache_index_page(self):
        response = self.authorized_client_no_edit.get('/')
        last_cache_post = response.content

        self.post = Post.objects.create(text='new', author=self.user_no_edit)

        response = self.authorized_client_no_edit.get('/')
        current_cache_post = response.content
        self.assertEqual(
            last_cache_post,
            current_cache_post,
            'Caching is not working properly.')

        cache.clear()

        response = self.authorized_client_no_edit.get('/')
        new_cache_post = response.content
        self.assertNotEqual(
            current_cache_post,
            new_cache_post,
            'Caching is not working.')
