# webstory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.webstory_list_view, name='webstory_list'),
    path('<slug:slug>/', views.webstory_detail_view, name='webstory_detail'),
]