from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.template.loader import render_to_string
from webstory.models import WebStory
from blog.models import Post, Category
from django.conf import settings
import os


def about_page(request):
    return render(request, 'core/about.html')

def contact_page(request):
    return render(request, 'core/contact.html')

def disclaimer_page(request):
    return render(request, 'core/disclaimer.html')

def policy_page(request):
    return render(request, 'core/policy.html')

def terms_page(request):
    return render(request, 'core/terms-and-conditions.html')

def get_latest(model, field='published_date'):
    try:
        return model.objects.latest(field).__getattribute__(field)
    except:
        return timezone.now()


def ads_txt_view(request):
    ads_txt_path = os.path.join(settings.BASE_DIR, 'static', 'ads.txt')
    print(f"ads_txt_path:{ads_txt_path}")
    if os.path.exists(ads_txt_path):
        with open(ads_txt_path, 'r') as file:
            file_content = file.read()
        return HttpResponse(file_content, content_type="text/plain")
    else:
        # Handle case where ads.txt file is not found (e.g., return 404 or empty response)
        return HttpResponse("ads.txt not found", status=404, content_type="text/plain")


def custom_sitemap_index(request):
    base_url = request.build_absolute_uri('/')[:-1]  # removes trailing slash

    sitemaps = [
        {
            "location": f"{base_url}/post-sitemap.xml",
            "lastmod": get_latest(Post, 'published_date'),
        },
        {
            "location": f"{base_url}/category-sitemap.xml",
            "lastmod": get_latest(Category, 'updated_at'),  # use meaningful field if available
        },
        {
            "location": f"{base_url}/webstory-sitemap.xml",
            "lastmod": get_latest(WebStory, 'updated_at'),  # use meaningful field if available
        },
        {
            "location": f"{base_url}/pages-sitemap.xml",
        },
    ]

    xml = render_to_string("sitemap_index.xml", {"sitemaps": sitemaps})
    return HttpResponse(xml, content_type="application/xml")
