# blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post, Category # Ensure Category is imported
from influencer.models import Influencer


def home_view(request):
    seo = {
        'meta_title': "Bavaal - Latest Entertainment, Lifestyle & Celebrity Buzz",
        'meta_description': "Explore entertainment, health, lifestyle, and celebrity stories. Stay updated with viral news and celebrity insights.",
        'keywords': "Bavaal, entertainment, lifestyle, health, celebrity news, viral, movies, influencers",
        'canonical_url': request.build_absolute_uri(),
        'og_description': "Catch up with Bavaal's trending entertainment, lifestyle tips, health updates, and celebrity gossips.",
        'og_type': "website",
        'og_image': None,  # Replace with image instance if needed, e.g., from a model
        'twitter_card': "summary_large_image",
        'twitter_title': "Bavaal - Latest Trends in Entertainment & Lifestyle",
        'twitter_description': "Your daily dose of celebrity buzz, lifestyle tips and health updates at Bavaal.",
        'twitter_image': None,  # Same as above
    }
    influencers = Influencer.objects.order_by('-created_at')[:4]

    return render(request, 'home.html', {'seo': seo, 'influencers': influencers,})
    
def blog_list(request):
    selected_category_slug = request.GET.get('category') # Get the category slug from the URL

    if selected_category_slug:
        # If a category is selected, filter posts by that category
        try:
            category = Category.objects.get(slug=selected_category_slug)
            # Removed 'published=True' filter as it does not exist in your Post model
            posts = Post.objects.filter(categories=category).order_by('-published_date')
        except Category.DoesNotExist:
            # Handle case where category slug is invalid (e.g., show all posts)
            posts = Post.objects.all().order_by('-published_date')
            selected_category_slug = None # Clear selected slug if category not found
            # You might consider adding a Django messages framework notification here for the user
    else:
        # If no category is selected, show all posts
        # Removed 'published=True' filter
        posts = Post.objects.all().order_by('-published_date')

    # Fetch all categories to display in the filter section of the template
    categories = Category.objects.all().order_by('name')

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category_slug': selected_category_slug,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    # Retrieve the post based on slug
    post = get_object_or_404(Post, slug=slug)
    canonical_url = request.build_absolute_uri(post.get_absolute_url())
    seo = {
        'canonical_url' : canonical_url,
        'og_type' :  'article',
        'twitter_card' : 'summary_large_image',
        'image': request.build_absolute_uri(post.featured_image.url) if post.featured_image else None,

    }
    # If you only want to show posts where published_date is in the past,
    # you would add a filter here, e.g., published_date__lte=timezone.now()
    return render(request, 'blog/blog_detail.html', {'post': post, 'seo': seo})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(categories=category).order_by('-published_date')
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts
    })
