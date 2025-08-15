from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post, Category
from webstory.models import WebStory
from influencer.models import Influencer
from django.conf import settings

class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.published_date

    def location(self, obj):
        return reverse('blog_detail', kwargs={'slug': obj.slug})


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.order_by('id')

    def location(self, obj):
        return reverse('category_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.updated_at

class InfluencersSitemap(Sitemap):
          
    def items(self):
        return Influencer.objects.order_by('id')

    def location(self, obj):
        return reverse('profile_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.created_at
    
    def get_urls(self, page=1, site=None, protocol=None):
        # Force localhost when in DEBUG mode
        if settings.DEBUG:
            class DummySite:
                domain = "127.0.0.1:8000"
                name = "localhost"
            site = DummySite()
            protocol = "http"
        return super().get_urls(page=page, site=site, protocol=protocol)

class WebstorySitemap(Sitemap):
    def items(self):
        return WebStory.objects.order_by('id')

    def location(self, obj):
        return reverse('webstory_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.created_at

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        return [
            'image-grid',
            'about',
            'contact',
            'privacy-policy',
            'terms-and-conditions',
            'disclaimer',
        ]
        
    def location(self, item):
        return reverse(item)