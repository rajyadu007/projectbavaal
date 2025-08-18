from django.urls import path
from . import views # Import your views from the same app

urlpatterns = [
    path('influencer/create/', views.create_or_update_influencer_profile, name='create_influencer_profile'),
    
    # URL for updating an existing influencer profile
    path('influencer/edit/<slug:slug>/', views.create_or_update_influencer_profile, name='update_influencer_profile'),


    #path('', views.profile_detail, name='profile_detail'),
]