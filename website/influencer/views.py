from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from .models import Influencer, Category
from django.core.management import call_command
from django.urls import reverse
from django.contrib import messages # Import messages framework
from django.core.files import File # For saving files from URLs
import requests # For making HTTP requests to fetch images
import os
from io import BytesIO # To handle image data in memory

from .forms import InfluencerProfileForm
from .models import Influencer

def create_or_update_influencer_profile(request, slug=None):
    """
    View to create a new influencer profile or update an existing one.
    Handles all text-based data and direct file uploads for profile_pic and poster_pic.
    """
    influencer = None
    if slug:
        influencer = get_object_or_404(Influencer, slug=slug)

    if request.method == 'POST':
        # When handling file uploads, always pass request.FILES to the form
        form = InfluencerProfileForm(request.POST, request.FILES, instance=influencer)
        if form.is_valid():
            # ModelForm handles saving the file fields automatically when form.save() is called
            influencer_instance = form.save()
            messages.success(request, "Influencer profile saved successfully!")
            return redirect('profile_detail', slug=influencer_instance.slug) # Use 'profile_detail' as per your project urls
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # For GET request, create an empty form or pre-fill it for update
        form = InfluencerProfileForm(instance=influencer)

    context = {
        'form': form,
        'influencer': influencer,
        'page_title': "Create Influencer Profile" if not influencer else f"Edit {influencer.name}'s Profile",
        'form_description': "Fill out the influencer's details and upload profile and poster pictures.",
    }
    return render(request, 'influencer/influencer_profile_form.html', context)


def influencer_detail(request, slug):
    """
    A simple view to display influencer details.
    """
    influencer = get_object_or_404(Influencer, slug=slug)
    context = {
        'influencer': influencer,
        'page_title': f"{influencer.name}'s Profile",
    }
    return render(request, 'influencer/influencer_detail.html', context)




def profile_detail(request, slug): # Changed from pk to slug
    """
    Displays the detail page for an influencer, fetched by their slug.
    """
    influencer = get_object_or_404(Influencer, slug=slug) # Fetch by slug
    return render(request, 'influencer/profile.html', {'influencer': influencer}) # Renders the portfolio.html with influencer data


def influencer_portfolio_view(request):
    return render(request, 'influencer/portfolio.html')