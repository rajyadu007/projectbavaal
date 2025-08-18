# your_app_name/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Influencer, Category

class InfluencerProfileForm(forms.ModelForm):
    """
    Form for creating/updating Influencer profiles.
    Now handles direct file uploads for profile_pic and poster_pic.
    """
    class Meta:
        model = Influencer
        # Include actual ImageField model fields for direct file upload
        fields = [
            'name',
            'slug',
            'profile_pic', # Now handles file upload directly
            'poster_pic',  # Now handles file upload directly
            'full_name',
            'nickname',
            'date_of_birth',
            'place_of_birth',
            'height_cm',
            'hair_color',
            'eye_color',
            'education',
            'profession',
            'biography',
            'profile_summary',
            'instagram_handle',
            'instagram_followers',
            'youtube_channel',
            'tiktok_handle',
            'twitter_handle',
            'brand_collaborations',
            'media_appearances',
            'businesses',
            'hobbies',
            'estimated_net_worth',
            'assets',
            'achievements',
            'public_perception',
            'controversies',
            'categories',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 5}),
            'profile_summary': forms.Textarea(attrs={'rows': 3}),
            'brand_collaborations': forms.Textarea(attrs={'rows': 3}),
            'media_appearances': forms.Textarea(attrs={'rows': 3}),
            'businesses': forms.Textarea(attrs={'rows': 3}),
            'hobbies': forms.Textarea(attrs={'rows': 3}),
            'assets': forms.Textarea(attrs={'rows': 3}),
            'public_perception': forms.Textarea(attrs={'rows': 3}),
            'controversies': forms.Textarea(attrs={'rows': 3}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'categories': 'Hold Ctrl/Cmd to select multiple categories.',
            'slug': 'A unique, URL-friendly version of the name. Leave blank to auto-generate.'
        }

    def clean_slug(self):
        """
        Custom validation for the slug field.
        Ensures uniqueness for user-provided slugs, or auto-generates if empty.
        """
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')

        if not slug and name:
            slug = slugify(name)
        elif slug:
            slug = slugify(slug)
        
        if slug:
            qs = Influencer.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError(f"This slug '{slug}' is already taken. Please choose a different one or leave it blank to auto-generate.")
        
        return slug

    def save(self, commit=True):
        """
        Overrides save to ensure slug is generated if not provided and valid.
        """
        instance = super().save(commit=False)
        
        if not instance.slug and instance.name:
            instance.slug = slugify(instance.name)
            base_slug = instance.slug
            num = 1
            while Influencer.objects.filter(slug=instance.slug).exists() and \
                  (self.instance is None or Influencer.objects.get(pk=self.instance.pk).slug != instance.slug):
                instance.slug = f"{base_slug}-{num}"
                num += 1

        if commit:
            instance.save()
            self.save_m2m() # Crucial for ManyToMany fields like 'categories'
        return instance

