
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserEditForm
from django.urls import reverse

posts = [
    {
        'id': 0,
        'location': 'Остров отчаянья',
        'date': '30 сентября 1659 года',
        'category': 'travel',
        'text': '''Наш корабль, застигнутый в открытом море
                страшным штормом, потерпел крушение.
                Весь экипаж, кроме меня, утонул; я же,
                несчастный Робинзон Крузо, был выброшен
                полумёртвым на берег этого проклятого острова,
                который назвал островом Отчаяния.''',
    },
    {
        'id': 1,
        'location': 'Остров отчаянья',
        'date': '1 октября 1659 года',
        'category': 'not-my-day',
        'text': '''Проснувшись поутру, я увидел, что наш корабль сняло
                с мели приливом и пригнало гораздо ближе к берегу.
                Это подало мне надежду, что, когда ветер стихнет,
                мне удастся добраться до корабля и запастись едой и
                другими необходимыми вещами. Я немного приободрился,
                хотя печаль о погибших товарищах не покидала меня.
                Мне всё думалось, что, останься мы на корабле, мы
                непременно спаслись бы. Теперь из его обломков мы могли бы
                построить баркас, на котором и выбрались бы из этого
                гиблого места.''',
    },
    {
        'id': 2,
        'location': 'Остров отчаянья',
        'date': '25 октября 1659 года',
        'category': 'not-my-day',
        'text': '''Всю ночь и весь день шёл дождь и дул сильный
                порывистый ветер. 25 октября.  Корабль за ночь разбило
                в щепки; на том месте, где он стоял, торчат какие-то
                жалкие обломки,  да и те видны только во время отлива.
                Весь этот день я хлопотал  около вещей: укрывал и
                укутывал их, чтобы не испортились от дождя.''',
    },
]


def index(request):
    post_qs = Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments')).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_qs, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'post_list': page_obj.object_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        id=id,
    )
    # Hide unpublished/future posts from others, allow author to see
    is_visible = (
        post.is_published and
        (post.category is None or post.category.is_published) and
        post.pub_date <= timezone.now()
    )
    if not is_visible and request.user != post.author:
        return render(request, 'pages/404.html', status=404)
    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_qs = Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments')).filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_qs, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj, 'post_list': page_obj.object_list}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('category', 'location', 'author').annotate(
        comment_count=Count('comments')
    ).filter(
        author=user
    ).order_by('-pub_date')
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
        'post_list': page_obj.object_list,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', id=post.id)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        if request.user == post.author or request.user.is_staff:
            post.delete()
            return redirect('blog:index')
        return redirect('blog:post_detail', id=post.id)
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_comment(request, id, comment_id):
    post = get_object_or_404(Post, id=id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post.id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {'form': form, 'post': post, 'comment': comment})


@login_required
def delete_comment(request, id, comment_id):
    post = get_object_or_404(Post, id=id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if request.method == 'POST':
        if request.user == comment.author or request.user.is_staff:
            comment.delete()
            return redirect('blog:post_detail', id=post.id)
        return redirect('blog:post_detail', id=post.id)
    # Reuse comment template for confirmation without passing a form in context
    return render(request, 'blog/comment.html', {'post': post, 'comment': comment})


@login_required
def edit_profile(request, username=None):
    form = UserEditForm(instance=request.user)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})
