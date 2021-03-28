import textwrap as tw

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.constants import field_help_texts, field_verboses
from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create(
                username='tester', password='password'),
            text=('Some love is just a lie of the heart'
                  'The cold remains of what began'
                  'with a passionate start'
                  'And they may not want it to end'
                  'But it will its just a question of when'),)

    def test_verbose_name(self):
        post = PostModelTest.post

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_str(self):
        post = PostModelTest.post
        answer = [
            post.author,
            post.group,
            post.pub_date,
            tw.shorten(post.text, 15), ]
        self.assertEqual(str(post), f'{answer}')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test',
            slug='test-group',
            description='test1',)

    def test_group_str(self):
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AnnaY')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Some love is just a lie of the heart',)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Perfect song',)

    def test_comment_str(self):
        comment = CommentModelTest.comment
        self.assertEqual(str(comment), f'{comment.author, comment.text}')
