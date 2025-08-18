# your_app_name/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory 
from django.utils.text import slugify
from .models import Influencer, Category, InfluencerTweet, InfluencerImage, InfluencerVideo

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


# --- Forms for related models ---
class InfluencerImageForm(forms.ModelForm):
    class Meta:
        model = InfluencerImage
        fields = ['image_url', 'caption', 'display_order']
        widgets = {
            'image_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'display_order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'})
        }
    
    # IMPORTANT: Make fields not required at the form level
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_url'].required = False
        self.fields['caption'].required = False
        # display_order is PositiveIntegerField with default=0, it's not truly optional if 0 is considered a value.
        # If display_order should also be completely optional, you'd need to adjust its model definition as well.


class InfluencerVideoForm(forms.ModelForm):
    class Meta:
        model = InfluencerVideo
        fields = ['source', 'video_url', 'caption', 'display_order']
        widgets = {
            'source': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'video_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'display_order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'})
        }

    # IMPORTANT: Make fields not required at the form level
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source'].required = False
        self.fields['video_url'].required = False
        self.fields['caption'].required = False


class InfluencerTweetForm(forms.ModelForm):
    class Meta:
        model = InfluencerTweet
        fields = ['tweet_url', 'caption', 'display_order']
        widgets = {
            'tweet_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'}),
            'display_order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:border-blue-300'})
        }

    # IMPORTANT: Make fields not required at the form level
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tweet_url'].required = False
        self.fields['caption'].required = False


# --- Formsets ---
# max_num=6 enforces the limit you requested.
# extra=1 means one empty form is shown initially for adding new items.
# can_delete=True adds a checkbox to delete existing items.
InfluencerImageFormSet = inlineformset_factory(Influencer, InfluencerImage, 
                                            form=InfluencerImageForm, extra=0, max_num=6, can_delete=True)
InfluencerVideoFormSet = inlineformset_factory(Influencer, InfluencerVideo, 
                                            form=InfluencerVideoForm, extra=0, max_num=3, can_delete=True)
InfluencerTweetFormSet = inlineformset_factory(Influencer, InfluencerTweet, 
                                            form=InfluencerTweetForm, extra=0, max_num=4, can_delete=True)

