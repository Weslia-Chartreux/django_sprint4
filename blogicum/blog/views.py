from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from blog.forms import CommentForm, PostForm, ProfileForm
from blog.models import Category, Comment, Post
from blog.utils import posts_pagination, query_post


def index(request):
    """
    Отображает главную страницу блога со списком опубликованных постов.
    
    Использует пагинацию для отображения ограниченного количества постов на странице.
    Возвращает шаблон index.html с контекстом, содержащим page_obj для пагинации.
    """
    page_obj = posts_pagination(request, query_post())
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    """
    Отображает страницу с постами определенной категории.
    
    Args:
        category_slug (str): URL-слаг категории для фильтрации постов.
    
    Возвращает:
        Страницу категории с постами, относящимися к указанной категории.
        Если категория не существует или не опубликована, возвращает 404.
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    page_obj = posts_pagination(
        request,
        query_post(manager=category.posts)
    )
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def post_detail(request, post_id):
    """
    Отображает детальную страницу поста со всеми комментариями.
    
    Args:
        post_id (int): ID поста для отображения.
    
    Особенности:
        - Проверяет права доступа: если пользователь не автор поста,
          показывает только опубликованные посты.
        - Отображает форму для добавления новых комментариев.
        - Сортирует комментарии по дате создания (от старых к новым).
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        post = get_object_or_404(query_post(), id=post_id)
    comments = post.comments.order_by('created_at')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'blog/detail.html', context)


@login_required
def create_post(request):
    """
    Обрабатывает создание нового поста в блоге.
    
    Требует аутентификации пользователя. При успешном создании поста
    перенаправляет на страницу профиля автора.
    
    Поддерживает загрузку файлов через FILES. При GET-запросе отображает
    пустую форму, при POST - валидирует и сохраняет данные.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    """
    Редактирование существующего поста.
    
    Args:
        post_id (int): ID поста для редактирования.
    
    Требования:
        - Пользователь должен быть аутентифицирован.
        - Только автор поста может его редактировать.
    
    При попытке редактирования чужого поста происходит перенаправление
    на страницу детального просмотра поста.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """
    Удаление поста из блога.
    
    Args:
        post_id (int): ID поста для удаления.
    
    Процесс:
        - Подтверждение удаления через POST-запрос.
        - Только автор может удалить свой пост.
        - При GET-запросе отображает форму подтверждения.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def profile(request, username):
    """
    Отображает профиль пользователя с его постами.
    
    Args:
        username (str): Имя пользователя, чей профиль нужно отобразить.
    
    Особенности:
        - Показывает все посты пользователя.
        - Для неавторизованных пользователей или чужих профилей
          показываются только опубликованные посты.
        - Использует пагинацию для списка постов.
    """
    profile = get_object_or_404(User, username=username)
    posts = query_post(manager=profile.posts, filters=profile != request.user)
    page_obj = posts_pagination(request, posts)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """
    Редактирование профиля текущего пользователя.
    
    Требует аутентификации. Позволяет пользователю изменить свои данные.
    При успешном сохранении перенаправляет на страницу своего профиля.
    """
    form = ProfileForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def add_comment(request, post_id):
    """
    Добавляет новый комментарий к указанному посту.
    
    Args:
        post_id (int): ID поста, к которому добавляется комментарий.
    
    Требует аутентификации. Автоматически устанавливает автора комментария
    как текущего пользователя. После добавления перенаправляет на страницу поста.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """
    Редактирование существующего комментария.
    
    Args:
        post_id (int): ID поста, к которому относится комментарий.
        comment_id (int): ID комментария для редактирования.
    
    Ограничения:
        - Только автор комментария может его редактировать.
        - При попытке редактирования чужого комментария происходит
          перенаправление на страницу поста.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """
    Удаление комментария.
    
    Args:
        post_id (int): ID поста, к которому относится комментарий.
        comment_id (int): ID комментария для удаления.
    
    Процесс:
        - Требует подтверждения через POST-запрос.
        - Только автор может удалить свой комментарий.
        - При GET-запросе отображает страницу подтверждения.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
