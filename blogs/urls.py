from django.urls import path

from blogs.views import blog_add, blog_detail, blog_list

urlpatterns = [
    path('', blog_list, name='blog_list'),
    path('add/', blog_add, name='blog_add'),
    path('<int:pk>/', blog_detail, name='blog_detail'),
]
