# your_app_name/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse 
import uuid
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Category(models.Model):
    """
    Represents a category or niche an influencer specializes in.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the category (e.g., 'Lifestyle', 'Fashion')")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

def profile_pic_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.slug}-profile.{ext}"
    return os.path.join("influencers", "profile_pics", filename)

def poster_pic_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.slug}-poster.{ext}"
    return os.path.join("influencers", "poster_pics", filename)

class Influencer(models.Model):
    # Basic Identification
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    profile_pic = models.ImageField(upload_to=profile_pic_upload_path, blank=True, null=True)
    poster_pic = models.ImageField(upload_to=poster_pic_upload_path, blank=True, null=True)

    # Personal Details
    full_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hair_color = models.CharField(max_length=50, blank=True, null=True)
    eye_color = models.CharField(max_length=50, blank=True, null=True)

    # Education & Career
    education = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)

    # Biography & Summary
    biography = models.TextField(blank=True, null=True, help_text="Detailed life & career history")
    profile_summary = models.TextField(blank=True, null=True, help_text="Short, inspiring overview of the influencer")

    # Social Media Stats
    instagram_handle = models.CharField(max_length=255, blank=True, null=True)
    instagram_followers = models.PositiveIntegerField(blank=True, null=True)
    youtube_channel = models.CharField(max_length=255, blank=True, null=True)
    tiktok_handle = models.CharField(max_length=255, blank=True, null=True)
    twitter_handle = models.CharField(max_length=255, blank=True, null=True)

    # Brand Collaborations & Media Appearances
    brand_collaborations = models.TextField(blank=True, null=True)
    media_appearances = models.TextField(blank=True, null=True)

    # Entrepreneurial Ventures
    businesses = models.TextField(blank=True, null=True)

    # Lifestyle & Hobbies
    hobbies = models.TextField(blank=True, null=True)

    # Financial & Assets
    estimated_net_worth = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    assets = models.TextField(blank=True, null=True)

    # Public Perception & Impact
    achievements = models.TextField(blank=True, null=True)
    public_perception = models.TextField(blank=True, null=True)
    controversies = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Influencer.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---- Related Models for Media ---- #

class InfluencerImage(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(help_text="Direct Instagram image link")
    caption = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.influencer.name}"


class InfluencerVideo(models.Model):
    VIDEO_SOURCE_CHOICES = [
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram Reels'),
    ]
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name="videos")
    source = models.CharField(max_length=20, choices=VIDEO_SOURCE_CHOICES)
    video_url = models.URLField(help_text="YouTube or Instagram video link")
    caption = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.source.capitalize()} video for {self.influencer.name}"


class InfluencerTweet(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name="tweets")
    tweet_url = models.URLField(help_text="Full Twitter/X post link")
    caption = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Tweet for {self.influencer.name}"
    
# ------------------------------
# File Cleanup Signals
# ------------------------------

def delete_file_if_exists(file_field):
    """Helper to delete file from storage."""
    if file_field and file_field.name and file_field.storage.exists(file_field.name):
        file_field.delete(save=False)


@receiver(post_delete, sender=Influencer)
def delete_influencer_main_images(sender, instance, **kwargs):
    delete_file_if_exists(instance.profile_pic)
    delete_file_if_exists(instance.poster_pic)


@receiver(post_delete, sender=InfluencerImage)
def delete_related_image_file(sender, instance, **kwargs):
    delete_file_if_exists(instance.image)