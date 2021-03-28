import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_group_0 = post_object.group
        post_text_0 = post_object.text
        post_image_0 = post_object.image
        post_pub_date_0 = post_object.pub_date
        self.assertEqual(post_author_0, PostViewsTest.post.author)
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_group_0, PostViewsTest.post.group)
        self.assertEqual(post_image_0, PostViewsTest.post.image)
        self.assertEqual(post_pub_date_0, PostViewsTest.post.pub_date)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group',
                args=[PostViewsTest.group.slug])
        )
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_group_0 = post_object.group
        post_text_0 = post_object.text
        post_image_0 = post_object.image
        post_pub_date_0 = post_object.pub_date
        self.assertEqual(post_author_0, PostViewsTest.post.author)
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_group_0, PostViewsTest.post.group)
        self.assertEqual(post_image_0, PostViewsTest.post.image)
        self.assertEqual(post_pub_date_0, PostViewsTest.post.pub_date)

    def test_new_post_show_correct_context(self):
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

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                args=[PostViewsTest.post.author])
        )
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_group_0 = post_object.group
        post_text_0 = post_object.text
        post_image_0 = post_object.image
        post_pub_date_0 = post_object.pub_date
        self.assertEqual(post_author_0, PostViewsTest.post.author)
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_group_0, PostViewsTest.post.group)
        self.assertEqual(post_image_0, PostViewsTest.post.image)
        self.assertEqual(post_pub_date_0, PostViewsTest.post.pub_date)

    def test_post_id_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post',
                args=[PostViewsTest.post.author, PostViewsTest.post.pk])
        )
        post_object = response.context['post']
        post_author_0 = post_object.author
        post_group_0 = post_object.group
        post_text_0 = post_object.text
        post_image_0 = post_object.image
        post_pub_date_0 = post_object.pub_date
        self.assertEqual(post_author_0, PostViewsTest.post.author)
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_group_0, PostViewsTest.post.group)
        self.assertEqual(post_image_0, PostViewsTest.post.image)
        self.assertEqual(post_pub_date_0, PostViewsTest.post.pub_date)

        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client_for_edit.get(
            reverse(
                'posts:post_edit',
                args=[PostViewsTest.post.author, PostViewsTest.post.pk])
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

    def test_follow_page_show_correct_context(self):
        follow_count = Follow.objects.count()

        self.follow = Follow.objects.create(
            user=PostViewsTest.user_for_follow,
            author=PostViewsTest.user_for_edit
        )
        self.assertTrue(Follow.objects.count(), follow_count + 1)

        response = PostViewsTest.authorized_client_for_follow.get(
            reverse('posts:follow_index'))

        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_group_0 = post_object.group
        post_text_0 = post_object.text
        post_image_0 = post_object.image
        post_pub_date_0 = post_object.pub_date
        self.assertEqual(post_author_0, PostViewsTest.post.author)
        self.assertEqual(post_text_0, PostViewsTest.post.text)
        self.assertEqual(post_group_0, PostViewsTest.post.group)
        self.assertEqual(post_image_0, PostViewsTest.post.image)
        self.assertEqual(post_pub_date_0, PostViewsTest.post.pub_date)

        response = self.authorized_client.get(
            reverse('posts:follow_index'))

        self.assertFalse(response.context['page'])

        self.unfollow = Follow.objects.filter(
            user=PostViewsTest.user_for_follow,
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
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_4 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_5 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_6 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_7 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_8 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_9 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_10 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_11 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_12 = Post.objects.create(
            author=cls.user,
            text='test1',
            group=cls.group,
            pub_date='12.03.2021',)
        cls.post_13 = Post.objects.create(
            author=cls.user,
            text='test1',
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
