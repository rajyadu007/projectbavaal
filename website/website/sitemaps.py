from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post, Category
from webstory.models import WebStory

class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.published_date

    def location(self, obj):
        return reverse('blog_detail', kwargs={'slug': obj.slug})


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.updated_at


class WebstorySitemap(Sitemap):
    def items(self):
        return WebStory.objects.all()

    def location(self, obj):
        return reverse('webstory:webstory_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.created_at
