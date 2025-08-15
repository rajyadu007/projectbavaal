from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """Extract YouTube ID from URL"""
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None