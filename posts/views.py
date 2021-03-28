from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .constants import page_amount
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, page_amount)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        {'page': page, }
    )


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, page_amount)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'page': page, 'group': group, }
    )


@login_required
def new_post(request):
    is_new = True
    if request.method != 'POST':
        form = PostForm()
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'is_new': is_new, })

    form = PostForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'is_new': is_new, })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_all = author.posts.all()
    following = Follow.objects.filter(author=author)
    paginator = Paginator(posts_all, page_amount)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/profile.html',
        {'page': page,
         'post': posts_all,
         'author': author,
         'following': following, }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    comments = post.comments.all()
    comments_show = True
    form = CommentForm()
    return render(
        request,
        'posts/post.html',
        {'post': post,
         'author': author,
         'comments': comments,
         'form': form,
         'comments_show': comments_show, })


@login_required
def post_edit(request, username, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post', username, post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if request.method != 'POST':
        form = PostForm(instance=post)
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'post': post, 'is_edit': is_edit, })

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'post': post, 'is_edit': is_edit, })

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:post', username, post_id)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != 'POST':
        form = CommentForm()
        return render(
            request,
            'comments.html',
            {'form': form, 'post': post, })

    form = CommentForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'comments.html',
            {'form': form, })

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    author_list = User.objects.filter(following__author__following__user=True)
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, page_amount)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page,
         'paginator': paginator,
         'post': post_list,
         'author': author_list, }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
