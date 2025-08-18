# admin.py
from django.contrib import admin
from .models import Influencer, InfluencerImage, InfluencerVideo, InfluencerTweet

class BaseAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        """Show all field names dynamically"""
        return [field.name for field in self.model._meta.fields]

    def get_readonly_fields(self, request, obj=None):
        """Make auto fields (like id, created_at) read-only"""
        return [f.name for f in self.model._meta.fields if f.auto_created]


@admin.register(Influencer)
class InfluencerAdmin(BaseAdmin):
    pass


@admin.register(InfluencerImage)
class InfluencerImageAdmin(BaseAdmin):
    pass


@admin.register(InfluencerVideo)
class InfluencerVideoAdmin(BaseAdmin):
    pass

@admin.register(InfluencerTweet)
class InfluencerTweetAdmin(BaseAdmin):
    pass
