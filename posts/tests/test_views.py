import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
MEDIA_ROOT = tempfile.mkdtemp()


def context_pages(self, context_dict, response):
    post_object = response.context[context_dict][0]
    post_author = post_object.author
    post_group = post_object.group
    post_text = post_object.text
    post_image = post_object.image
    post_pub_date = post_object.pub_date
    return (
        self.assertEqual(post_author, PostViewsTest.post.author),
        self.assertEqual(post_text, PostViewsTest.post.text),
        self.assertEqual(post_group, PostViewsTest.post.group),
        self.assertEqual(post_image, PostViewsTest.post.image),
        self.assertEqual(post_pub_date, PostViewsTest.post.pub_date),)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test',
            slug='test-group',
            description='test1',
        )
        cls.user_for_edit = User.objects.create_user(username='SashaS')
        cls.authorized_client_for_edit = Client()
        cls.authorized_client_for_edit.force_login(cls.user_for_edit)
        cls.user_for_follow = User.objects.create_user(username='TashaS')
        cls.authorized_client_for_follow = Client()
        cls.authorized_client_for_follow.force_login(cls.user_for_follow)

        cls.follow = Follow.objects.create(
            user=cls.user_for_follow,
            author=cls.user_for_edit
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',)

        cls.post = Post.objects.create(
            author=cls.user_for_edit,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',
            image=uploaded,)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Kirill')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_index_page_shows_corrext_context(self):
        context_pages(
            self,
            context_dict='page',
            response=self.authorized_client_for_follow.get(
                reverse('posts:index')))

    def test_group_page_shows_correct_context(self):
        context_pages(
            self,
            context_dict='page',
            response=self.authorized_client_for_follow.get(
                reverse(
                    'posts:group',
                    args=[PostViewsTest.group.slug, ])))

    def test_profile_page_shows_correct_context(self):
        context_pages(
            self,
            context_dict='page',
            response=self.authorized_client_for_follow.get(
                reverse(
                    'posts:profile',
                    args=[PostViewsTest.post.author, ])))

    def test_follow_page_shows_correct_context(self):
        context_pages(
            self,
            context_dict='page',
            response=self.authorized_client_for_follow.get(
                reverse('posts:follow_index',)))

    def test_post_id_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post',
                args=[PostViewsTest.post.author, PostViewsTest.post.pk])
        )

        post_object = response.context['post']
        post_author = post_object.author
        post_group = post_object.group
        post_text = post_object.text
        post_image = post_object.image
        post_pub_date = post_object.pub_date
        self.assertEqual(post_author, PostViewsTest.post.author)
        self.assertEqual(post_text, PostViewsTest.post.text)
        self.assertEqual(post_group, PostViewsTest.post.group)
        self.assertEqual(post_image, PostViewsTest.post.image)
        self.assertEqual(post_pub_date, PostViewsTest.post.pub_date)

        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_show_correct_context_field(self):
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context_field(self):
        response = self.authorized_client_for_edit.get(
            reverse(
                'posts:post_edit',
                args=[PostViewsTest.post.author, PostViewsTest.post.pk, ])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_comment_for_authorized(self):
        comment_count = Comment.objects.count()

        self.comment = Comment.objects.create(
            post=PostViewsTest.post,
            author=self.user,
            text='Testing text',
        )
        self.assertTrue(Comment.objects.count(), comment_count + 1)

    def test_comment_for_anonymous(self):
        response = self.guest_client.get(reverse(
            'posts:add_comment',
            args=[PostViewsTest.post.author, PostViewsTest.post.pk, ]))
        self.assertEqual(response.status_code, 302)

    def test_follow_for_authorized(self):
        follow_count = Follow.objects.count()

        self.follow = Follow.objects.create(
            user=self.user,
            author=PostViewsTest.user_for_edit
        )
        self.assertTrue(Follow.objects.count(), follow_count + 1)

    def test_follow_for_anonymous(self):
        response = self.guest_client.get(reverse(
            'posts:profile_follow',
            args=[PostViewsTest.post.author, ]))
        self.assertEqual(response.status_code, 302)

    def test_unfollow_for_authorized(self):
        follow_count = Follow.objects.count()

        self.follow = Follow.objects.create(
            user=self.user,
            author=PostViewsTest.user_for_edit
        )
        self.assertTrue(Follow.objects.count(), follow_count + 1)

        self.unfollow = Follow.objects.filter(
            user=self.user,
            author=PostViewsTest.user_for_edit).delete()

        self.assertEqual(Follow.objects.count(), follow_count)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SashaS')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test',
            slug='test-group',
            description='test1')
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'test{i}',
                group=cls.group,
                pub_date='12.03.2021',)

    def test_index_first_page_containse_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_index_second_page_containse_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_group_first_page_containse_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group',
                args=[PaginatorTest.group.slug])
        )
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_group_second_page_containse_three_records(self):
        response = self.client.get(
            reverse(
                ('posts:group'), args=[PaginatorTest.group.slug]) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
