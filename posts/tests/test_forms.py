import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.constants import form_data_for_edit
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Post

User = get_user_model()


class PostCreateEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='AnnaY')
        cls.post = Post.objects.create(text='Tododo', author=cls.user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        post_count = Post.objects.count()

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
            content_type='image/gif'
        )
        form_data_for_new = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data_for_new,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        post_object = PostCreateEditFormTests.post
        username = post_object.author
        post_id = post_object.pk
        post_count = Post.objects.count()

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', args=[username, post_id]),
            data=form_data_for_edit,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post',
                             args=[PostCreateEditFormTests.post.author,
                                   PostCreateEditFormTests.post.pk]))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data_for_edit['text'],
            ).exists()
        )


class CommentCreatedFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CommentForm()
        cls.user = User.objects.create_user(username='AnnaY')
        cls.post = Post.objects.create(text='Tododo', author=cls.user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()

    def test_create_comment(self):
        comment_count = Comment.objects.count()

        form_data_for_comment = {
            'text': 'Тестовый текст',
            'author': CommentCreatedFormTests.user,
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[
                CommentCreatedFormTests.post.author,
                CommentCreatedFormTests.post.pk, ],),
            data=form_data_for_comment,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post',
            args=[
                CommentCreatedFormTests.post.author,
                CommentCreatedFormTests.post.pk, ])
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст',
                author=CommentCreatedFormTests.user,
            ).exists()
        )
