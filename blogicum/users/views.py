from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.paginator import Paginator

from blog.models import Post

User = get_user_model()


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'


def profile(request, username):
    """Страница профиля пользователя."""
    profile_user = get_object_or_404(User, username=username)
    
    if request.user == profile_user:
        # Автор видит все свои посты
        posts = Post.objects.filter(author=profile_user).select_related(
            'category', 'location', 'author'
        ).order_by('-pub_date')
    else:
        # Остальные видят только опубликованные
        from django.utils import timezone
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location', 'author').order_by('-pub_date')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile.html', context)
