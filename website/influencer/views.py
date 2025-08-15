from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import os
import subprocess
from django.conf import settings
from .models import Influencer, Category
from django.core.management import call_command

YAML_FILE_PATH = os.path.join(settings.BASE_DIR, "influencer_data.yaml")

def yaml_upload_view(request):
    if request.method == "POST":
        yaml_data = request.POST.get("yaml_content")
        with open(YAML_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(yaml_data)

        # ✅ Run the management command directly inside Django
        try:
            call_command("fill_dummy_influencer", YAML_FILE_PATH)
            messages.success(request, "Influencer data saved and published!")
        except Exception as e:
            messages.error(request, f"Error running command: {e}")

        return redirect("yaml_upload")

    # If file exists, load it
    yaml_content = ""
    if os.path.exists(YAML_FILE_PATH):
        with open(YAML_FILE_PATH, "r", encoding="utf-8") as f:
            yaml_content = f.read()

    return render(request, "influencer/yaml_upload.html", {
        "yaml_content": yaml_content
    })

def profile_detail(request, slug): # Changed from pk to slug
    """
    Displays the detail page for an influencer, fetched by their slug.
    """
    influencer = get_object_or_404(Influencer, slug=slug) # Fetch by slug
    return render(request, 'influencer/profile.html', {'influencer': influencer}) # Renders the portfolio.html with influencer data


def influencer_portfolio_view(request):
    return render(request, 'influencer/portfolio.html')