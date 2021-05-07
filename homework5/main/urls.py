"""Настройки маршрутизатора."""
from django.conf.urls import url
from django.urls import path
from django.views.generic import RedirectView, TemplateView

from . import views

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='static/assets/img/favicon/favicon.ico')),
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home_page'),
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about_page'),

    path('posts/', views.PostsListView.as_view(), name='post_list'),
    path('posts/<int:author_id>/', views.author_posts, name='posts_by_author'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/show/<int:post_id>/', views.post_show, name='post_show'),
    path('posts/update/<int:post_id>/', views.post_update, name='post_update'),

    path('authors/new/', views.authors_new, name='authors_new'),
    path('authors/all/', views.authors_all, name='authors_all'),
    path('author/subscribe/', views.author_subscribe, name='author_subscribe'),
    path('author/subscribers/all/', views.author_subscribers_all, name='author_subscribers_all'),

    path('author/books/', views.books_all, name='books_all'),
    path('author/categories/', views.categories_all, name='categories_all'),

    path('api/posts/', views.json_posts, name='json_posts'),
    path('api/post/<int:post_id>/', views.api_post_show, name='api_post_show'),
    path('api/subscribe/', views.api_subscribe, name='api_subscribe'),
    path('api/subscribers/all/', views.api_subscribers_all, name='api_subscribers_all'),
    path('api/authors/all/', views.api_authors_all, name='api_authors_all'),
    path('api/authors/new/', views.api_authors_new, name='api_authors_new'),

    path('logs_delete/', views.test, name='test'),

    path('contact-us/create/', views.CreateContactUsView.as_view(), name='contact_us'),

    path('parser/medusweet/', views.medusweet_xlsx, name='medusweet_xlsx')
]
