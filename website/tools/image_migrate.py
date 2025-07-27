import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.conf import settings
from django.utils.text import slugify


def download_image(img_url, local_dir):
    try:
        parsed_url = urlparse(img_url)
        filename = os.path.basename(parsed_url.path)
        name, ext = os.path.splitext(filename)
        safe_filename = slugify(name) + ext

        local_path = os.path.join(local_dir, safe_filename)
        full_path = os.path.join(settings.MEDIA_ROOT, local_path)

        if not os.path.exists(full_path):
            response = requests.get(img_url, stream=True, timeout=10)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"✅ Downloaded: {img_url}")
            else:
                print(f"❌ Failed: {img_url} | {response.status_code}")
                return None

        return f"{settings.MEDIA_URL}{local_path}"
    except Exception as e:
        print(f"❌ Error downloading {img_url}: {e}")
        return None


def migrate_images_in_post(post):
    soup = BeautifulSoup(post.content, "html.parser")
    local_dir = f"uploads/post_images/{post.id}"
    updated = False

    for img in soup.find_all("img"):
        # --- Handle src ---
        src = img.get("src")
        if src and src.startswith("http"):
            new_src = download_image(src, local_dir)
            if new_src:
                img["src"] = new_src
                updated = True

        # --- Handle srcset ---
        srcset = img.get("srcset")
        if srcset:
            new_srcset_list = []
            for part in srcset.split(","):
                try:
                    url_part, size = part.strip().rsplit(" ", 1)
                    new_url = download_image(url_part.strip(), local_dir)
                    if new_url:
                        new_srcset_list.append(f"{new_url} {size}")
                except ValueError:
                    continue

            if new_srcset_list:
                img["srcset"] = ", ".join(new_srcset_list)
                updated = True

    if updated:
        post.content = str(soup)
        post.save()
        print("✅ Post content updated with local image references.")
