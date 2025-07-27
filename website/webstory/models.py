from django.db import models

class WebStory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()  # Full AMP HTML
    cover_image = models.ImageField(upload_to="webstories/cover/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug: # If slug is empty or None
            original_slug = slugify(self.title)
            queryset = WebStory.objects.all()
            if self.pk: # Exclude self when updating
                queryset = queryset.exclude(pk=self.pk)

            # Ensure slug is unique by appending a number if necessary
            unique_slug = original_slug
            num = 1
            while queryset.filter(slug=unique_slug).exists():
                unique_slug = f"{original_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class WebStoryImage(models.Model):
    story = models.ForeignKey(WebStory, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="webstories/images/")
    alt = models.CharField(max_length=255, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.story.title}"
