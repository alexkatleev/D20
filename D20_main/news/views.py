from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.views.generic import ListView, UpdateView, DeleteView

from .models import Post, Category, BaseRegisterForm, Author, Comment
from .forms import PostForm, CommentForm
from .filter import PostFilter
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages


@login_required
def upgrade_me(request):
    Author.objects.create(user_author=request.user)
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(request.user)
    return redirect('/news/')


def send_notifications(preview, pk, title, subscribers):
    html_contect = render_to_string(
        'post_add_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['aleksTest13@yandex.ru'],    # тут пишем to=subscribe для отправки на почту подписчикам, для теста моя
    )
    # print(settings.DEFAULT_FROM_EMAIL)
    msg.attach_alternative(html_contect, 'text/html')
    msg.send()


class PostList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-date_in'
    template_name = 'news.html'
    context_object_name = 'post_news'
    paginate_by = 5

    def get_context_data(self,
                         **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())  # вписываем фильтр в контекст
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый пост
            form.save()

        return super().get(request, *args, **kwargs)


class PostDetailAndCommentCreate(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'onenews.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(pk=self.kwargs['pk'])
        context['comments'] = Comment.objects.filter(post_comment=context['post'], approved=True)
        return context

    def form_valid(self, form):
        object_ = form.save(commit=False)
        object_.post_comment = Post.objects.get(pk=self.kwargs['pk'])
        object_.user_comment = self.request.user

        # Определение темы письма и текста сообщения
        subject = 'Новый комментарий к посту'
        message = f'Пользователь {self.request.user.username} оставил новый комментарий к посту {self.get_success_url()}'

        # Получение всех зарегистрированных пользователей
        users = User.objects.all()

        # Отправка письма каждому пользователю
        for user in users:
            send_mail(
                subject,  # тема письма
                message,  # текст сообщения
                settings.DEFAULT_FROM_EMAIL,  # отправитель
                [user.email],  # получатель(и)  для тестов пишу свою
                fail_silently=False,  # не подавлять исключения при ошибках
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['pk']})


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'news.post_add'
    form_class = PostForm
    model = Post
    template_name = 'post_add.html'


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.post_edit'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


# дженерик для удаления поста
class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.post_delete'
    model = Post
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    context_object_name = 'post_delete'


class PostSearch(ListView):  # поиск поста
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'post_news'
    paginate_by = 50

    def get_queryset(self):  # получаем обычный запрос
        queryset = super().get_queryset()  # используем наш класс фильтрации
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-date_in')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):  # создание комментария
    model = Comment
    fields = ['content']
    template_name = 'comm_create.html'
    success_url = reverse_lazy('post_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post_id = self.kwargs['pk']
        form.instance.parent_id = self.request.POST.get('parent_id', None)
        return super().form_valid(form)


class CommentListView(LoginRequiredMixin, ListView):  # отображения списка комментариев пользователя
    model = Comment
    template_name = 'comm_list.html'
    context_object_name = 'comments'

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(user=user)


class CommentFilterView(LoginRequiredMixin, ListView):  # фильтрации комментариев по постам
    model = Comment
    template_name = 'comm_list.html'
    context_object_name = 'comments'

    def get_queryset(self):
        user = self.request.user
        post_id = self.kwargs['pk']
        return Comment.objects.filter(user=user, post_id=post_id)


class CommentDeleteView(LoginRequiredMixin, DeleteView):  # удаления комментария
    model = Comment
    success_url = reverse_lazy('comm_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Комментарий удален')
        return super().delete(request, *args, **kwargs)


class CommentApproveView(LoginRequiredMixin, DeleteView):  # принятия комментария
    model = Comment
    success_url = reverse_lazy('comm_list')

    def approve(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.approved = True
        self.object.save()
        messages.success(request, 'Комментарий добавлен')
        return super().delete(request, *args, **kwargs)


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = 'вы подписались на категорию: '
    return render(request, 'subscribe.html', {'category': category, 'message': message})


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)
    message = 'отписка от категории: '
    return render(request, 'subscribe.html', {'category': category, 'message': message})

