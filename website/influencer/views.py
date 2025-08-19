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
from .models import Influencer, InfluencerCommunityPost, PostNotification
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string

from .forms import (
    InfluencerProfileForm,
    InfluencerImageFormSet, # Import the formsets
    InfluencerVideoFormSet,
    InfluencerTweetFormSet,
    CommunityPostForm,
)

def influencer_community_view(request, influencer_id):
    influencer = get_object_or_404(Influencer, id=influencer_id)
    posts = influencer.community_posts.filter(parent__isnull=True, is_approved=True)

    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.influencer = influencer
            post.save()

            # Notify parent user if this is a reply
            if post.parent:
                PostNotification.objects.create(post=post, user=post.parent.user)

            return redirect('influencer_community', influencer_id=influencer.id)
    else:
        form = CommunityPostForm()

    return render(request, 'community/influencer_community.html', {
        'influencer': influencer,
        'posts': posts,
        'form': form
    })


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

@login_required
def profile_detail(request, slug):
    influencer = get_object_or_404(Influencer, slug=slug)
    posts = influencer.community_posts.filter(parent__isnull=True, is_approved=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent')
        parent_post = None
        if parent_id:
            parent_post = InfluencerCommunityPost.objects.filter(id=parent_id).first()

        if content:
            new_post = InfluencerCommunityPost.objects.create(
                influencer=influencer,
                user=request.user,
                parent=parent_post,
                content=content
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('influencer/_community_post.html', {'post': new_post}, request)
                return JsonResponse({
                    'success': True,
                    'html': html,
                    'is_reply': bool(parent_post),
                    'parent_id': parent_post.id if parent_post else None,
                })

            return redirect('profile_detail', slug=slug)

    return render(request, 'influencer/profile.html', {'influencer': influencer, 'posts': posts})

def influencer_portfolio_view(request):
    return render(request, 'influencer/portfolio.html')