# blog/urls.py
from django.urls import path
from . import views # Import views from the current app (blog)

urlpatterns = [
    path('', views.home_view, name='home'), # This will map to example.com/
    path('blogs/', views.blog_list, name='blog_list'), # This will map to example.com/blogs/
    path('<slug:slug>/', views.blog_detail, name='blog_detail'), # This will map to example.com/your-blog-post-slug/
    path('category/<slug:slug>/', views.category_detail, name='category_detail'), # This will map to example.com/category/your-category-slug/
]