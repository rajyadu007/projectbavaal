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
from .models import Influencer
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .forms import (
    InfluencerProfileForm,
    InfluencerImageFormSet, # Import the formsets
    InfluencerVideoFormSet,
    InfluencerTweetFormSet,
)

@login_required
def create_or_update_influencer_profile(request, slug=None):
    influencer = None
    if slug:
        influencer = get_object_or_404(Influencer, slug=slug)

    if request.method == 'POST':
        form = InfluencerProfileForm(request.POST, request.FILES, instance=influencer)
        image_formset = InfluencerImageFormSet(request.POST, request.FILES, instance=influencer, prefix='images')
        video_formset = InfluencerVideoFormSet(request.POST, request.FILES, instance=influencer, prefix='videos')
        tweet_formset = InfluencerTweetFormSet(request.POST, request.FILES, instance=influencer, prefix='tweets')

        if form.is_valid() and image_formset.is_valid() and video_formset.is_valid() and tweet_formset.is_valid():
            try:
                with transaction.atomic():
                    influencer_instance = form.save()
                    image_formset.instance = influencer_instance
                    video_formset.instance = influencer_instance
                    tweet_formset.instance = influencer_instance

                    image_formset.save()
                    video_formset.save()
                    tweet_formset.save()

                messages.success(request, "Influencer profile and related links saved successfully!")
                return redirect('profile_detail', slug=influencer_instance.slug)
            except Exception as e:
                messages.error(request, f"An error occurred while saving: {e}")
        else:
           messages.error(request, "Please correct the errors below.")
    else:
        form = InfluencerProfileForm(instance=influencer)
        image_formset = InfluencerImageFormSet(instance=influencer, prefix='images')
        video_formset = InfluencerVideoFormSet(instance=influencer, prefix='videos')
        tweet_formset = InfluencerTweetFormSet(instance=influencer, prefix='tweets')

    context = {
        'form': form,
        'image_formset': image_formset,
        'video_formset': video_formset,
        'tweet_formset': tweet_formset,
        'influencer': influencer,
        'page_title': "Create Influencer Profile" if not influencer else f"Edit {influencer.name}'s Profile",
        'form_description': "Fill out the influencer's details and manage their images, videos, and tweets.",
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