from django.db import models
from django.contrib.auth.models import User
import os

def user_profile_image_path(instance, filename):

    # Clean the username by replacing @ with -
    cleaned_username = instance.user.username.replace('@', '-')
    
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Generate filename: cleaned_username_timestamp.random_ext
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{cleaned_username}_{timestamp}.{ext}"
    
    # Return full path
    return os.path.join('userprofile_pics', new_filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True)
    #bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"