from django.db import models
from django.utils.text import slugify

class SEOPage(models.Model):
    """
    Stores SEO metadata for specific pages identified by their URL path.
    Use '/' for home, or full relative paths like '/about/', '/blog/my-article/'.
    """

    # URL path for the page (used to match current request.path)
    path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique URL path for this SEO config (e.g. '/', '/about/', '/blog/my-post/')."
    )

    # Standard SEO Meta Tags
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Meta title (recommended: ≤ 60 characters)."
    )
    meta_description = models.TextField(
        blank=True,
        help_text="Meta description (recommended: ≤ 160 characters)."
    )
    canonical_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Canonical URL to avoid duplicate content."
    )

    # Open Graph Meta Tags
    OG_TYPE_CHOICES = [
        ('website', 'Website'),
        ('article', 'Article'),
        ('profile', 'Profile'),
        ('book', 'Book'),
        ('video.movie', 'Movie Video'),
        ('video.episode', 'Episode Video'),
    ]
    og_type = models.CharField(
        max_length=50,
        choices=OG_TYPE_CHOICES,
        default='website',
        help_text="Open Graph type (e.g., 'website', 'article')."
    )
    og_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Open Graph title for sharing on Facebook, LinkedIn, etc."
    )
    og_description = models.TextField(
        blank=True,
        help_text="Open Graph description for social media previews."
    )
    og_image = models.ImageField(
        upload_to='seo_images/og/',
        blank=True,
        null=True,
        help_text="Open Graph image (recommended: 1200x630)."
    )

    # Twitter Card Meta Tags
    TWITTER_CARD_CHOICES = [
        ('summary', 'Summary Card'),
        ('summary_large_image', 'Summary Card with Large Image'),
        ('app', 'App Card'),
        ('player', 'Player Card'),
    ]
    twitter_card = models.CharField(
        max_length=50,
        choices=TWITTER_CARD_CHOICES,
        default='summary_large_image',
        help_text="Twitter card type."
    )
    twitter_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Title for Twitter card."
    )
    twitter_description = models.TextField(
        blank=True,
        help_text="Description for Twitter card."
    )
    twitter_image = models.ImageField(
        upload_to='seo_images/twitter/',
        blank=True,
        null=True,
        help_text="Image for Twitter card."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO Page"
        verbose_name_plural = "SEO Pages"
        ordering = ['path']
        indexes = [
            models.Index(fields=["path"]),
        ]

    def __str__(self):
        return f"SEO for: {self.path}"

    def get_absolute_url(self):
        return self.path

    def save(self, *args, **kwargs):
        # Normalize the path to start with '/' and strip trailing slash unless it's the root '/'
        if self.path and not self.path.startswith('/'):
            self.path = '/' + self.path
        if self.path != '/' and self.path.endswith('/'):
            self.path = self.path.rstrip('/')
        super().save(*args, **kwargs)
