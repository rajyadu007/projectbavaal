from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.contrib.sitemaps.views import sitemap
from . import sitemaps as sm 
from . import views 
from influencer.views import profile_detail

sitemaps = {
    'post': sm.PostSitemap,
    'category': sm.CategorySitemap,
    'webstory' : sm.WebstorySitemap,
}

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # CKEditor URLs
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # AllAuth URLs
    path('accounts/', include('allauth.urls')),

    # Webstory App URLspath('about/', about_page, name='about'),
    path("web-stories/", include("webstory.urls")),

    # Influencer Profile URL (if you want it directly here)
    # This pattern catches anything starting with '@' followed by a slug
    re_path(r'^@(?P<slug>[-\w]+)/$', profile_detail, name='profile_detail'),

    # Sitemap URLs
    # Use the 'sitemaps' dictionary directly in the sitemap view
    path('ads.txt', views.ads_txt_view, name='ads_txt'),
    path('sitemap_index.xml', views.custom_sitemap_index, name='custom_sitemap_index'), # Pass sitemaps to your custom index
    path('<section>-sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # IMPORTANT: The root URL should point to ONE primary app.
    # Typically, your 'blog' app might handle the root.
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('disclaimer/', views.disclaimer_page, name='disclaimer'),
    path('privacy-policy/', views.policy_page, name='privacy-policy'),
    path('terms-and-conditions/', views.terms_page, name='terms-and-conditions'),
    path('', include('blog.urls')), # This should be the last 'include' for the root, or place specific paths above it.
]

# Serve media files only in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)