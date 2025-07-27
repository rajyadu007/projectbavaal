from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Influencer, SuggestedInfluencerEdit, Category

def profile_detail(request, slug): # Changed from pk to slug
    """
    Displays the detail page for an influencer, fetched by their slug.
    """
    influencer = get_object_or_404(Influencer, slug=slug) # Fetch by slug
    return render(request, 'influencer/profile.html', {'influencer': influencer}) # Renders the portfolio.html with influencer data


def influencer_portfolio_view(request):
    return render(request, 'influencer/portfolio.html')