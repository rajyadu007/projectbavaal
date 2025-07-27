# webstory/admin.py
from django.contrib import admin
from django.utils.html import format_html # Import format_html for displaying image thumbnails
from .models import WebStory, WebStoryImage

# 1. Define an inline for WebStoryImage
# This allows you to add/edit WebStoryImage objects directly from the WebStory's admin page.
class WebStoryImageInline(admin.TabularInline): # You can also use admin.StackedInline for a different layout
    model = WebStoryImage
    extra = 1 # Number of empty forms to display for adding new images
    fields = ('image', 'alt', 'width', 'height', 'order') # Fields to show in the inline form

# 2. Register the WebStory model with its custom Admin class
@admin.register(WebStory)
class WebStoryAdmin(admin.ModelAdmin):
    # Fields to display in the list view of Web Stories in the admin
    list_display = ('title', 'slug', 'created_at', 'cover_image_thumbnail')
    
    # Automatically populate the slug field based on the title as you type
    prepopulated_fields = {'slug': ('title',)}
    
    # Enable search functionality for these fields in the admin list view
    search_fields = ('title', 'content')
    
    # Add filters to the sidebar for easy navigation
    list_filter = ('created_at',)
    
    # Include the WebStoryImageInline to manage related images directly
    inlines = [WebStoryImageInline]

    # Custom method to display a thumbnail of the cover image in the list view
    def cover_image_thumbnail(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="auto" style="border-radius: 4px;" />', obj.cover_image.url)
        return "No Cover"
    cover_image_thumbnail.short_description = 'Cover' # Column header for the thumbnail

# If you wanted to register WebStoryImage as a standalone model in the admin,
# you would use the following line (but the inline is generally preferred for this relationship):
# admin.site.register(WebStoryImage)