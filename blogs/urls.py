from django.urls import path

from blogs.views import blog_add, blog_delete, blog_detail, blog_edit, blog_list, comment_add

urlpatterns = [
    path('', blog_list, name='blog_list'),
    path('add/', blog_add, name='blog_add'),
    path('<int:pk>/edit/', blog_edit, name='blog_edit'),
    path('<int:pk>/delete/', blog_delete, name='blog_delete'),
    path('<int:pk>/comments/add/', comment_add, name='comment_add'),
    path('<int:pk>/', blog_detail, name='blog_detail'),
]
