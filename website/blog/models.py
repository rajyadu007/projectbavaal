# blog/models.py
from django.db import models
from django.utils.text import slugify
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO
from django.urls import reverse

class Author(models.Model):
    wp_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    wp_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name
    
    def lastmod(self, obj):
        return obj.updated_at # Or obj.last_updated if you have one

class Tag(models.Model):
    wp_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name



class Post(models.Model):
    wp_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_description = models.TextField(blank=True)
    excerpt = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=255, blank=True, null=True, help_text="Alt text for SEO and accessibility")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    noindex = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def generate_og_image(self):
            image_path = self.featured_image.path
            image = Image.open(image_path)

            # Resize to OG dimensions: 1200x630
            image = image.convert("RGB")
            image = image.resize((1200, 630), Image.ANTIALIAS)

            buffer = BytesIO()
            image.save(fp=buffer, format='JPEG')

            og_image_name = f"og_{os.path.basename(self.featured_image.name)}"
            self.og_image.save(og_image_name, ContentFile(buffer.getvalue()), save=False)

            self.save(update_fields=['og_image'])