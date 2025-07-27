# your_app_name/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings # Import settings to reference AUTH_USER_MODEL
from django.contrib.auth import get_user_model # To get the active user model
from django.utils.text import slugify


# Get the active User model
User = get_user_model()


class SuggestedInfluencerEdit(models.Model):
    """
    Stores suggested edits for an Influencer profile made by users other than the influencer themselves.
    These suggestions require admin validation before being applied.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='suggested_edits',
                                   help_text="The influencer profile this edit suggestion is for.")
    
    # The user who made the suggestion (can be any logged-in user)
    suggested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     help_text="The user who submitted this suggestion.")
    
    # Timestamp of when the suggestion was made
    suggested_at = models.DateTimeField(auto_now_add=True)
    
    # Status of the suggestion
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING',
                              help_text="Current status of the suggested edit.")

    # --- Fields for suggested changes (add fields here for whatever can be edited) ---
    # You would add fields here that correspond to the fields in the Influencer model
    # that you want to allow "other users" to suggest edits for.
    # For example:

    suggested_name = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="Suggested new name for the influencer.")
    suggested_bio = models.TextField(blank=True, null=True,
                                     help_text="Suggested new biography for the influencer.")
    suggested_blog_content = CKEditor5Field(blank=True, null=True,
                                           help_text="Suggested new blog content (rich text).")
    # Add more fields as needed, e.g.:
    # suggested_instagram_url = models.URLField(max_length=200, blank=True, null=True)
    # suggested_followers_count = models.BigIntegerField(blank=True, null=True)

    # Admin comments/reason for approval/rejection
    admin_notes = models.TextField(blank=True, help_text="Notes from the admin regarding approval/rejection.")

    class Meta:
        verbose_name = "Suggested Influencer Edit"
        verbose_name_plural = "Suggested Influencer Edits"
        ordering = ['-suggested_at'] # Order by most recent suggestions first

    def __str__(self):
        return f"Edit for {self.influencer.name} by {self.suggested_by.username if self.suggested_by else 'Anonymous'} ({self.status})"

    def apply_edit(self):
        """
        Applies the suggested changes to the actual Influencer model.
        This method should only be called after admin approval.
        """
        influencer = self.influencer
        if self.suggested_name is not None:
            influencer.name = self.suggested_name
        if self.suggested_bio is not None:
            influencer.bio = self.suggested_bio
        if self.suggested_blog_content is not None:
            influencer.blog_content = self.suggested_blog_content
        # Add more fields to apply here
        influencer.save()
        self.status = 'APPROVED'
        self.save()

    def reject_edit(self, admin_notes=""):
        """
        Marks the suggested edit as rejected.
        """
        self.status = 'REJECTED'
        self.admin_notes = admin_notes
        self.save()


# Model for influencer categories (e.g., Lifestyle, Fashion, Beauty)
class Category(models.Model):
    """
    Represents a category or niche an influencer specializes in.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the category (e.g., 'Lifestyle', 'Fashion')")

    class Meta:
        verbose_name_plural = "Categories" # Correct plural name for admin interface

    def __str__(self):
        return self.name

# Model for individual content pieces (e.g., YouTube videos, Instagram posts)
class Content(models.Model):
    """
    Represents a piece of content (e.g., video, photo, short) created by an influencer.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='contents',
                                   help_text="The influencer who created this content.")
    title = models.CharField(max_length=255, help_text="Title of the content (e.g., 'Summer Outfit Ideas 2023')")
    
    # URL to the external content (YouTube video, Instagram post, TikTok video, etc.)
    external_url = models.URLField(max_length=500, help_text="Direct link to the external content (YouTube, Instagram, etc.)")
    
    # Thumbnail image for the content
    thumbnail = models.ImageField(upload_to='content_thumbnails/', blank=True, null=True,
                                  help_text="Thumbnail image for the content.")
    
    views_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                         help_text="Number of views for this content.")
    likes_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                        help_text="Number of likes for this content.")
    
    # Optional: content type (e.g., 'Video', 'Image', 'Short', 'Reel')
    CONTENT_TYPES = [
        ('VIDEO', 'Video'),
        ('IMAGE', 'Image'),
        ('SHORT', 'Short Video'),
        ('REEL', 'Reel'),
        ('POST', 'Text Post'),
    ]
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='VIDEO',
                                    help_text="Type of content.")

    published_date = models.DateField(blank=True, null=True, help_text="Date the content was published.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Contents"
        ordering = ['-published_date'] # Order by most recent content first

    def __str__(self):
        return f"{self.title} by {self.influencer.name}"

# Model for brand collaborations
class Collaboration(models.Model):
    """
    Represents a brand collaboration an influencer has participated in.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='collaborations',
                                   help_text="The influencer involved in this collaboration.")
    campaign_name = models.CharField(max_length=255, help_text="Name of the collaboration campaign (e.g., 'Sephora Summer Collection')")
    
    # URL to the external collaboration post/page
    external_url = models.URLField(max_length=500, help_text="Direct link to the external collaboration post or campaign page.")
    
    # Thumbnail image for the collaboration
    thumbnail = models.ImageField(upload_to='collaboration_thumbnails/', blank=True, null=True,
                                  help_text="Thumbnail image for the collaboration.")
    
    # "2.0M People Engaged" can be stored as a string or broken down
    engagement_metric = models.CharField(max_length=100, blank=True, help_text="Metric showing engagement (e.g., '2.0M People Engaged')")
    
    start_date = models.DateField(blank=True, null=True, help_text="Start date of the collaboration.")
    end_date = models.DateField(blank=True, null=True, help_text="End date of the collaboration (optional).")
    
    is_sponsored = models.BooleanField(default=True, help_text="Indicates if this is a sponsored collaboration.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date'] # Order by most recent collaboration first

    def __str__(self):
        return f"{self.campaign_name} with {self.influencer.name}"


# Main Influencer Model (updated with related_name for Contents and Collaborations)
class Influencer(models.Model):
    # Link to Django's built-in User model.
    # OneToOneField ensures one user can claim one influencer profile.
    # null=True, blank=True allows for influencers who haven't claimed their page yet.
    # on_delete=models.SET_NULL means if the user is deleted, the influencer profile remains,
    # but the 'user' field becomes NULL.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='influencer_profile',
                                help_text="The user account linked to this influencer profile (if claimed).")

    slug = models.SlugField(unique=True, blank=True)
    # --- Basic Information ---
    name = models.CharField(max_length=255, help_text="Full name of the influencer")
    unique_id = models.CharField(max_length=50, unique=True, blank=True, null=True,
                                 help_text="A unique identifier for the influencer (e.g., 'ID: 1224567')")
    bio = models.TextField(blank=True, help_text="A short biography or description of the influencer")
    
    # Using ImageField requires Pillow to be installed (pip install Pillow)
    # Ensure MEDIA_ROOT and MEDIA_URL are configured in your Django settings.py
    profile_image = models.ImageField(upload_to='influencer_profiles/', blank=True, null=True,
                                      help_text="Profile picture of the influencer")
    
    # Influencer 'type' (e.g., Calb, Mega, Macro, Nano)
    INFLUENCER_TYPES = [
        ('NANO', 'Nano (1k-10k followers)'),
        ('MICRO', 'Micro (10k-100k followers)'),
        ('MACRO', 'Macro (100k-1M followers)'),
        ('MEGA', 'Mega (1M+ followers)'),
        ('CALB', 'Celebrity/Brand (Large following, often public figures)'), # 'Calb' from template
    ]
    type = models.CharField(max_length=10, choices=INFLUENCER_TYPES, default='MICRO',
                            help_text="Category based on follower count or influence level")

    # --- Statistics ---
    # Using BigIntegerField for potentially large follower/like/view counts
    followers_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                             help_text="Total number of followers")
    likes_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                         help_text="Total number of likes across content")
    views_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                         help_text="Total number of views across content")
    posts_count = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                      help_text="Total number of posts/content pieces")
    
    # Rating out of 5 (e.g., 4.8)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0,
                                 validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
                                 help_text="Average rating of the influencer (out of 5.0)")
    
    collaborations_count = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                               help_text="Number of brand collaborations completed")

    # --- Social Media Links ---
    instagram_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to Instagram profile")
    tiktok_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to TikTok profile")
    youtube_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to YouTube channel")
    twitter_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to Twitter profile")
    
    # Rich text field for blog content
    blog_content = CKEditor5Field(blank=True, help_text="Full blog content with rich text formatting (e.g., headings, images, tables)")

    # --- Relationships ---
    # Many-to-Many relationship with Category model
    categories = models.ManyToManyField(Category, related_name='influencers', blank=True,
                                        help_text="Categories or niches associated with the influencer")

    # Note: Content and Collaboration models now have a ForeignKey back to Influencer,
    # so you access them via influencer.contents.all() and influencer.collaborations.all()
    # No need for ManyToMany here.

    # --- Timestamps (useful for tracking) ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name'] # Order influencers alphabetically by name by default

    def __str__(self):
        return self.name

    # You can add custom methods here, for example, to format counts
    def get_formatted_followers(self):
        if self.followers_count >= 1_000_000:
            return f"{self.followers_count / 1_000_000:.1f}M"
        elif self.followers_count >= 1_000:
            return f"{self.followers_count / 1_000:.1f}K"
        return str(self.followers_count)

    def get_formatted_likes(self):
        if self.likes_count >= 1_000_000:
            return f"{self.likes_count / 1_000_000:.1f}M"
        elif self.likes_count >= 1_000:
            return f"{self.likes_count / 1_000:.1f}K"
        return str(self.likes_count)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Influencer.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
