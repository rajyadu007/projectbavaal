# your_app_name/admin.py

from django.contrib import admin
# Import all your models
from .models import Category, Influencer, Content, Collaboration, SuggestedInfluencerEdit
# No explicit import for CKEditor5Widget is needed here for RichTextUploadingField in admin,
# as the field itself handles its widget.

# --- Inline Admin Classes for Influencer's related models ---
# These allow you to manage Content and Collaboration directly from the Influencer's admin page.
class ContentInline(admin.TabularInline): # Use TabularInline for a compact table layout
    model = Content
    extra = 1 # Number of empty forms to display
    fields = ('title', 'external_url', 'thumbnail', 'views_count', 'likes_count', 'content_type', 'published_date')
    # You might want to add a formfield_overrides here if Content.description was RichTextUploadingField

class CollaborationInline(admin.TabularInline): # Use TabularInline for a compact table layout
    model = Collaboration
    extra = 1
    fields = ('campaign_name', 'external_url', 'thumbnail', 'engagement_metric', 'start_date', 'end_date', 'is_sponsored')
    # You might want to add a formfield_overrides here if Collaboration.details was RichTextUploadingField

# --- Influencer Admin ---
@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'type', 'followers_count', 'rating', 'unique_id', 'user', 'created_at')
    list_filter = ('type', 'categories', 'user')
    search_fields = ('name', 'bio', 'unique_id', 'user__username') # Allows searching by linked username
    filter_horizontal = ('categories',) # Improves ManyToMany field display in admin

    fieldsets = (
        (None, {
            'fields': ('user', 'slug', 'name', 'unique_id', 'bio', 'profile_image', 'type', 'categories')
        }),
        ('Statistics', {
            'fields': ('followers_count', 'likes_count', 'views_count', 'posts_count', 'rating', 'collaborations_count')
        }),
        ('Social Media', {
            'fields': ('instagram_url', 'tiktok_url', 'youtube_url', 'twitter_url')
        }),
        ('Blog Content', {
            'fields': ('blog_content',),
        }),
    )
    inlines = [ContentInline, CollaborationInline] # Include the inline classes here

    # IMPORTANT: The formfield_overrides for CKEditorWidget is NOT needed for RichTextUploadingField
    # from django-ckeditor-5. The field handles its own widget.
    # If you had this from a previous CKEditor 4 setup, remove it:
    # formfield_overrides = {
    #     models.TextField: {'widget': CKEditorWidget},
    # }

    # The save_model override below was incorrect for InfluencerAdmin.
    # It was attempting to set 'suggested_by' on an Influencer object, which doesn't exist.
    # This method is typically used to perform actions when saving the *current* model.
    # If you need to set the user who *created* an Influencer, you'd do it differently,
    # often by overriding get_form or in a custom save method on the model itself.
    # For now, I'm removing it as it's not applicable here.
    # def save_model(self, request, obj, form, change):
    #     if not change:
    #         obj.suggested_by = request.user
    #     super().save_model(request, obj, form, change)


# --- SuggestedInfluencerEdit Admin ---
@admin.register(SuggestedInfluencerEdit)
class SuggestedInfluencerEditAdmin(admin.ModelAdmin):
    list_display = ('influencer', 'suggested_by', 'suggested_at', 'status')
    list_filter = ('status',)
    search_fields = ('influencer__name', 'suggested_by__username', 'suggested_bio')
    readonly_fields = ('influencer', 'suggested_by', 'suggested_at') # These fields are set on creation

    fieldsets = (
        (None, {
            'fields': ('influencer', 'suggested_by', 'suggested_at', 'status', 'admin_notes')
        }),
        ('Suggested Changes', {
            'fields': ('suggested_name', 'suggested_bio', 'suggested_blog_content'),
            'description': 'These are the proposed changes by the user.',
        }),
    )

    actions = ['approve_suggestions', 'reject_suggestions']

    def approve_suggestions(self, request, queryset):
        # Ensure only pending suggestions are approved
        approved_count = 0
        for suggestion in queryset:
            if suggestion.status == 'PENDING':
                suggestion.apply_edit() # Call the method on the model
                approved_count += 1
        if approved_count > 0:
            self.message_user(request, f"{approved_count} suggested edits approved and applied.")
        else:
            self.message_user(request, "No pending suggestions were selected for approval.", level='warning')
    approve_suggestions.short_description = "Approve selected pending suggested edits"

    def reject_suggestions(self, request, queryset):
        # Ensure only pending suggestions are rejected
        rejected_count = 0
        for suggestion in queryset:
            if suggestion.status == 'PENDING':
                suggestion.reject_edit(admin_notes="Rejected by admin action.")
                rejected_count += 1
        if rejected_count > 0:
            self.message_user(request, f"{rejected_count} suggested edits rejected.")
        else:
            self.message_user(request, "No pending suggestions were selected for rejection.", level='warning')
    reject_suggestions.short_description = "Reject selected pending suggested edits"

    # Override save_model for SuggestedInfluencerEditAdmin to set suggested_by on creation
    def save_model(self, request, obj, form, change):
        if not change: # Only set suggested_by when the object is first created
            obj.suggested_by = request.user
        super().save_model(request, obj, form, change)

# --- Registering other models if you want separate admin pages for them ---
# If you don't use inlines, you would register them like this:
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# @admin.register(Content)
# class ContentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'influencer', 'content_type', 'views_count', 'published_date')
#     list_filter = ('content_type', 'influencer')
#     search_fields = ('title', 'influencer__name')

# @admin.register(Collaboration)
# class CollaborationAdmin(admin.ModelAdmin):
#     list_display = ('campaign_name', 'influencer', 'is_sponsored', 'start_date', 'engagement_metric')
#     list_filter = ('is_sponsored', 'influencer')
#     search_fields = ('campaign_name', 'influencer__name')
