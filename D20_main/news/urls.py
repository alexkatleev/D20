from django.urls import path

from . import views
from .views import PostList, PostUpdateView, PostDeleteView, PostCreateView, PostSearch, BaseRegisterView, \
      CommentCreateView, CommentListView, CommentFilterView, CommentDeleteView, CommentApproveView, PostDetailAndCommentCreate
from django.contrib.auth.views import LoginView, LogoutView
from .views import upgrade_me, CategoryListView, subscribe, unsubscribe

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetailAndCommentCreate.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='post_add'),
    path('edit/<int:pk>', PostUpdateView.as_view(), name='post_edit'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('login/',
         LoginView.as_view(template_name='news/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name='news/logout.html'),
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(template_name='news/signup.html'),
         name='signup'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('categories/<int:pk>', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
    path('categories/<int:pk>/unsubscribe', unsubscribe, name='unsubscribe'),
    #path('<int:pk>/reply/', ReplyCreate.as_view(), name='comm_post'),
    #path('my_replies/', Replies.as_view(), name='comm_post'),
    #path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/', CommentListView.as_view(), name='comm_reply'),
    path('comments/filter/<int:pk>/', CommentFilterView.as_view(), name='comment_filter'),
    path('comments/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comments/approve/<int:pk>/', CommentApproveView.as_view(), name='comment_approve'),
]
 