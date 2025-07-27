# your_app_name/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse # Import reverse for get_absolute_url

# Get the active User model
User = get_user_model()


class SuggestedInfluencerEdit(models.Model):
    """
    Stores suggested edits for an Influencer profile made by users other than the influencer themselves.
    These suggestions require admin validation before being applied.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='suggested_edits',
                                   help_text="The influencer profile this edit suggestion is for.")
    
    suggested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    help_text="The user who submitted this suggestion.")
    
    suggested_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING',
                              help_text="Current status of the suggested edit.")

    suggested_name = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="Suggested new name for the influencer.")
    suggested_bio = models.TextField(blank=True, null=True,
                                     help_text="Suggested new biography for the influencer.")
    suggested_blog_content = CKEditor5Field(blank=True, null=True,
                                            help_text="Suggested new blog content (rich text).")
    # Consider adding a specific field for which field is being suggested for clarity in admin.
    # e.g., suggested_field = models.CharField(max_length=50, blank=True, null=True)

    admin_notes = models.TextField(blank=True, help_text="Notes from the admin regarding approval/rejection.")

    class Meta:
        verbose_name = "Suggested Influencer Edit"
        verbose_name_plural = "Suggested Influencer Edits"
        ordering = ['-suggested_at']

    def __str__(self):
        suggester = self.suggested_by.username if self.suggested_by else 'Anonymous'
        return f"Edit for {self.influencer.name} by {suggester} ({self.status})"

    def apply_edit(self):
        """
        Applies the suggested changes to the actual Influencer model.
        This method should only be called after admin approval.
        """
        if self.status != 'PENDING':
            raise ValueError("Cannot apply an edit that is not pending.")

        influencer = self.influencer
        # Only update if the suggested value is not None (meaning it was actually suggested)
        if self.suggested_name is not None and self.suggested_name != '': # Added check for empty string
            influencer.name = self.suggested_name
        if self.suggested_bio is not None and self.suggested_bio != '': # Added check for empty string
            influencer.bio = self.suggested_bio
        if self.suggested_blog_content is not None: # CKEditorField might return an empty string, handle as needed
            influencer.blog_content = self.suggested_blog_content
        
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


class Category(models.Model):
    """
    Represents a category or niche an influencer specializes in.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the category (e.g., 'Lifestyle', 'Fashion')")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Content(models.Model):
    """
    Represents a piece of content (e.g., video, photo, short) created by an influencer.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='contents',
                                   help_text="The influencer who created this content.")
    title = models.CharField(max_length=255, help_text="Title of the content (e.g., 'Summer Outfit Ideas 2023')")
    
    external_url = models.URLField(max_length=500, help_text="Direct link to the external content (YouTube, Instagram, etc.)")
    
    thumbnail = models.ImageField(upload_to='content_thumbnails/', blank=True, null=True,
                                   help_text="Thumbnail image for the content.")
    
    views_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                          help_text="Number of views for this content.")
    likes_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                         help_text="Number of likes for this content.")
    
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
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.title} by {self.influencer.name}"

class Collaboration(models.Model):
    """
    Represents a brand collaboration an influencer has participated in.
    """
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='collaborations',
                                   help_text="The influencer involved in this collaboration.")
    campaign_name = models.CharField(max_length=255, help_text="Name of the collaboration campaign (e.g., 'Sephora Summer Collection')")
    
    external_url = models.URLField(max_length=500, help_text="Direct link to the external collaboration post or campaign page.")
    
    thumbnail = models.ImageField(upload_to='collaboration_thumbnails/', blank=True, null=True,
                                   help_text="Thumbnail image for the collaboration.")
    
    # It's better to store numerical values for engagement if you ever want to sort/filter by it.
    # If the format "2.0M People Engaged" is strictly for display, you can keep CharField.
    # Otherwise, consider a BigIntegerField for the raw number and format in the template/model method.
    engagement_metric = models.CharField(max_length=100, blank=True, help_text="Metric showing engagement (e.g., '2.0M People Engaged')")
    
    start_date = models.DateField(blank=True, null=True, help_text="Start date of the collaboration.")
    end_date = models.DateField(blank=True, null=True, help_text="End date of the collaboration (optional).")
    
    is_sponsored = models.BooleanField(default=True, help_text="Indicates if this is a sponsored collaboration.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.campaign_name} with {self.influencer.name}"


class Influencer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='influencer_profile',
                                 help_text="The user account linked to this influencer profile (if claimed).")

    slug = models.SlugField(unique=True, blank=True, max_length=255) # Increased max_length for slug
    name = models.CharField(max_length=255, help_text="Full name of the influencer")
    unique_id = models.CharField(max_length=50, unique=True, blank=True, null=True,
                                  help_text="A unique identifier for the influencer (e.g., 'ID: 1224567')")
    bio = models.TextField(blank=True, help_text="A short biography or description of the influencer")
    
    profile_image = models.ImageField(upload_to='influencer_profiles/', blank=True, null=True,
                                       help_text="Profile picture of the influencer")
    
    INFLUENCER_TYPES = [
        ('NANO', 'Nano (1k-10k followers)'),
        ('MICRO', 'Micro (10k-100k followers)'),
        ('MACRO', 'Macro (100k-1M followers)'),
        ('MEGA', 'Mega (1M+ followers)'),
        ('CELEB', 'Celebrity (Public figure with large following)'), # Changed 'Calb' to 'CELEB' for clarity
    ]
    type = models.CharField(max_length=10, choices=INFLUENCER_TYPES, default='MICRO',
                            help_text="Category based on follower count or influence level")

    followers_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                             help_text="Total number of followers")
    likes_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                           help_text="Total number of likes across content")
    views_count = models.BigIntegerField(default=0, validators=[MinValueValidator(0)],
                                           help_text="Total number of views across content")
    posts_count = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                      help_text="Total number of posts/content pieces")
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0,
                                 validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
                                 help_text="Average rating of the influencer (out of 5.0)")
    
    collaborations_count = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                               help_text="Number of brand collaborations completed")

    instagram_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to Instagram profile")
    tiktok_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to TikTok profile")
    youtube_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to YouTube channel")
    twitter_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link to Twitter profile")
    
    blog_content = CKEditor5Field(blank=True, help_text="Full blog content with rich text formatting (e.g., headings, images, tables)")

    categories = models.ManyToManyField(Category, related_name='influencers', blank=True,
                                        help_text="Categories or niches associated with the influencer")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a particular influencer instance."""
        return reverse('influencer_detail', kwargs={'slug': self.slug}) # Assuming you have a URL pattern named 'influencer_detail'

    def get_formatted_followers(self):
        """Formats follower count for display (e.g., 1.2M, 24.5K)."""
        if self.followers_count >= 1_000_000:
            return f"{self.followers_count / 1_000_000:.1f}M"
        elif self.followers_count >= 1_000:
            return f"{self.followers_count / 1_000:.1f}K"
        return str(self.followers_count)

    def get_formatted_likes(self):
        """Formats likes count for display (e.g., 1.2M, 24.5K)."""
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