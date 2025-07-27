from django.urls import path
from . import views

urlpatterns = [
    path('image-grid/', views.index, name='image-grid'),
    path('upload/', views.upload_images, name='upload_images'),
    path('generate_word/', views.generate_word_document, name='generate_word_document'),
]