from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
import uuid
import os # Import the os module
from django.db.models.signals import post_delete
from django.dispatch import receiver
import datetime # Import datetime for age calculation
from django.core.exceptions import ValidationError # Import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone


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

    # Relationships
    categories = models.ManyToManyField(Category, related_name='influencers', blank=True,
                                        help_text="Select categories this influencer specializes in.")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Removed _old_profile_pic and _old_poster_pic attributes
    # and __init__ method as we will fetch the old instance directly in save()

    def save(self, *args, **kwargs):
        # Handle slug generation if not already set
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Influencer.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        
        # --- File Cleanup Logic for Replacements ---
        if self.pk: # Only if it's an existing object being updated
            try:
                # Get the existing instance from the database BEFORE saving the new data
                # This old_instance still holds references to the old file paths
                old_instance = Influencer.objects.get(pk=self.pk)

                # Check if profile_pic has changed
                if old_instance.profile_pic and self.profile_pic.name != old_instance.profile_pic.name:
                    # Delete the old file using its FieldFile object
                    old_instance.profile_pic.delete(save=False) # save=False prevents an extra save operation

                # Check if poster_pic has changed
                if old_instance.poster_pic and self.poster_pic.name != old_instance.poster_pic.name:
                    # Delete the old file using its FieldFile object
                    old_instance.poster_pic.delete(save=False)

            except Influencer.DoesNotExist:
                # This should ideally not happen if self.pk exists, but good for robustness
                pass

        super().save(*args, **kwargs) # Save the current instance with its new (or kept) files

    @property
    def age(self):
        """Calculates the current age based on date_of_birth."""
        if self.date_of_birth:
            today = datetime.date.today()
            age_calc = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age_calc
        return None

    def __str__(self):
        return self.name



# ---- Related Models for Media ---- #

class InfluencerImage(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(help_text="Direct Instagram image link")
    caption = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Enforce limit of 6 images per influencer when creating new ones
        if not self.pk: # This is a new object being created
            if self.influencer.images.count() >= 6:
                raise ValidationError("An influencer cannot have more than 6 images.")
        super().save(*args, **kwargs)


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
    
    def save(self, *args, **kwargs):
        # Enforce limit of 3 videos per influencer when creating new ones
        if not self.pk: # This is a new object being created
            if self.influencer.videos.count() >= 3:
                raise ValidationError("An influencer cannot have more than 3 videos.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.capitalize()} video for {self.influencer.name}"


class InfluencerTweet(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name="tweets")
    tweet_url = models.URLField(help_text="Full Twitter/X post link")
    caption = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Enforce limit of 4 tweets per influencer when creating new ones
        if not self.pk: # This is a new object being created
            if self.influencer.tweets.count() >= 4:
                raise ValidationError("An influencer cannot have more than 4 tweets.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tweet for {self.influencer.name}"
    
# ------------------------------
# File Cleanup Signals
# ------------------------------

# This helper is now specifically for FieldFile instances
def delete_file_if_exists(field_file_instance):
    """Helper to delete a FieldFile from storage."""
    # Check if the field_file_instance actually refers to a file that exists
    # and if its name is not empty (i.e., it's not a dummy file object)
    if field_file_instance and field_file_instance.name and field_file_instance.storage.exists(field_file_instance.name):
        field_file_instance.delete(save=False) # delete() method handles the storage interaction


@receiver(post_delete, sender=Influencer)
def delete_influencer_main_images_on_object_deletion(sender, instance, **kwargs):
    """Deletes profile and poster pics when an Influencer object is deleted."""
    # Pass the actual FieldFile objects to the helper
    delete_file_if_exists(instance.profile_pic)
    delete_file_if_exists(instance.poster_pic)

class InfluencerCommunityPost(models.Model):
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='community_posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now, editable=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    is_approved = models.BooleanField(default=True)  # for moderation

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.username} on {self.influencer.name}'

class PostNotification(models.Model):
    post = models.ForeignKey(InfluencerCommunityPost, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user to notify
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notify {self.user.username} about post {self.post.id}'
