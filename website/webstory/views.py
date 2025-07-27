# webstory/views.py
from django.shortcuts import get_object_or_404, render
from .models import WebStory # Ensure WebStory is imported

def webstory_list_view(request):
    # Fetch all web stories, ordered by creation date (newest first)
    stories = WebStory.objects.all().order_by('-created_at')
    return render(request, "webstories/webstory_list.html", {"stories": stories})


def webstory_detail_view(request, slug):
    story = get_object_or_404(WebStory, slug=slug)
    return render(request, "webstories/detail.html", {"story": story})