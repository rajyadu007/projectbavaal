from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import UserProfile

# ----------------------------
# Inline for UserProfile
# ----------------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('avatar_preview',)

    # Avatar thumbnail for inline
    def avatar_preview(self, instance):
        if instance.profile_picture:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:50%;" />',
                instance.profile_picture.url
            )
        return "No Image"
    avatar_preview.short_description = "Avatar Preview"

# ----------------------------
# Extend default User admin
# ----------------------------
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_avatar')

    # Avatar thumbnail in user list
    def get_avatar(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.profile_picture:
            return format_html(
                '<img src="{}" style="width:30px; height:30px; border-radius:50%;" />',
                obj.userprofile.profile_picture.url
            )
        return "-"
    get_avatar.short_description = "Avatar"

# Unregister original User admin and register new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# ----------------------------
# Optional: Separate UserProfile admin
# ----------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    # Avatar thumbnail for UserProfile admin
    def avatar_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:50%;" />',
                obj.profile_picture.url
            )
        return "-"
    avatar_preview.short_description = "Avatar"
