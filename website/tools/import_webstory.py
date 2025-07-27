import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.utils.text import slugify
from django.conf import settings
from webstory.models import WebStory, WebStoryImage


def download_image(img_url, slug, subfolder="images"):
    try:
        parsed = urlparse(img_url)
        filename = os.path.basename(parsed.path)
        name, ext = os.path.splitext(filename)
        safe_filename = slugify(name) + ext

        local_dir = f"webstories/{slug}/{subfolder}"
        local_path = os.path.join(local_dir, safe_filename)
        full_path = os.path.join(settings.MEDIA_ROOT, local_path)

        if not os.path.exists(full_path):
            r = requests.get(img_url, stream=True, timeout=10)
            if r.status_code == 200:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        return f"{settings.MEDIA_URL}{local_path}", local_path
    except Exception as e:
        print(f"Failed to download image: {img_url} => {e}")
        return None, None


def import_webstory_from_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {url}")
        return

    soup = BeautifulSoup(resp.content, "html.parser")
    story_tag = soup.find("amp-story")
    if not story_tag:
        print("No <amp-story> found.")
        return

    title = story_tag.get("title") or soup.title.string or "Untitled Story"
    slug = slugify(title)

    # Cover image
    poster_img_url = story_tag.get("poster-portrait-src")
    local_cover_url, cover_path = None, None
    if poster_img_url:
        local_cover_url, cover_path = download_image(poster_img_url, slug, "cover")

    # Save or update WebStory
    story_obj, created = WebStory.objects.update_or_create(
        slug=slug,
        defaults={
            "title": title,
            "content": "",  # we'll set after replacing images
        }
    )
    if cover_path:
        story_obj.cover_image.name = cover_path
        story_obj.save()

    # Clear old images if updating
    if not created:
        story_obj.images.all().delete()

    # Replace all amp-img with local and store info
    for i, img_tag in enumerate(story_tag.find_all("amp-img")):
        src = img_tag.get("src")
        if not src or not src.startswith("http"):
            continue

        local_src, relative_path = download_image(src, slug)
        if local_src:
            # Replace in HTML
            img_tag["src"] = local_src

            # Save image record
            WebStoryImage.objects.create(
                story=story_obj,
                image=relative_path,
                alt=img_tag.get("alt", ""),
                width=int(img_tag.get("width") or 0),
                height=int(img_tag.get("height") or 0),
                order=i
            )

    # Save final AMP content
    story_obj.content = str(story_tag)
    story_obj.save()

    print(f"✅ {'Created' if created else 'Updated'} WebStory: {story_obj.title}")
