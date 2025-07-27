from django.urls import path
from . import views # Import your views from the same app

urlpatterns = [
    #path('<str:slug>/', views.influencer_detail, name='influencer_detail'), # Changed to slug
    path('', views.profile_detail, name='profile_detail'),
]