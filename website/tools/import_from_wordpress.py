import os
import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")  # replace with your project settings
django.setup()

from blog.models import Post, Author, Category, Tag


def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if not default_storage.exists(save_path):
                default_storage.save(save_path, ContentFile(response.content))
            return default_storage.url(save_path)
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return url  # fallback to original


def download_and_replace_images(content, post_slug):
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue

        try:
            filename = os.path.basename(urlparse(src).path)
            local_path = f"post_images/{post_slug}/{filename}"
            new_url = download_image(src, local_path)
            img['src'] = new_url
        except Exception as e:
            print(f"Failed to process image {src}: {e}")
            continue

    return str(soup)


def get_or_create_author(author_data):
    author, _ = Author.objects.get_or_create(
        wp_id=author_data["id"],
        defaults={"name": author_data["name"], "slug": author_data["slug"]}
    )
    return author


def get_or_create_category(cat_data):
    category, _ = Category.objects.get_or_create(
        wp_id=cat_data["id"],
        defaults={"name": cat_data["name"], "slug": cat_data["slug"]}
    )
    return category


def get_or_create_tags(tag_ids):
    tag_objs = []
    for tag_id in tag_ids:
        res = requests.get(f"https://bavaal.com/wp-json/wp/v2/tags/{tag_id}")
        if res.status_code == 200:
            tag_data = res.json()
            tag, _ = Tag.objects.get_or_create(
                wp_id=tag_data["id"],
                defaults={"name": tag_data["name"], "slug": tag_data["slug"]}
            )
            tag_objs.append(tag)
    return tag_objs


def import_posts():
    print("Fetching posts...")
    page = 1
    while True:
        response = requests.get(f"https://bavaal.com/wp-json/wp/v2/posts?per_page=10&page={page}")
        if response.status_code != 200:
            break

        posts = response.json()
        if not posts:
            break

        for post_data in posts:
            print(f"Importing: {post_data['title']['rendered']}")

            # Author
            author_data = requests.get(f"https://bavaal.com/wp-json/wp/v2/users/{post_data['author']}").json()
            author = get_or_create_author(author_data)

            # Category
            category = None
            if post_data["categories"]:
                cat_data = requests.get(f"https://bavaal.com/wp-json/wp/v2/categories/{post_data['categories'][0]}").json()
                category = get_or_create_category(cat_data)

            # Content
            raw_content = post_data["content"]["rendered"]
            updated_content = download_and_replace_images(raw_content, post_data["slug"])

            # Featured Image
            featured_image_url = None
            if post_data.get("featured_media"):
                media_data = requests.get(f"https://bavaal.com/wp-json/wp/v2/media/{post_data['featured_media']}").json()
                featured_image_url = media_data.get("source_url")

            post, created = Post.objects.get_or_create(
                wp_id=post_data["id"],
                defaults={
                    "title": post_data["title"]["rendered"],
                    "slug": post_data["slug"],
                    "content": updated_content,
                    "excerpt": post_data["excerpt"]["rendered"],
                    "author": author,
                    "published_date": datetime.strptime(post_data["date"], "%Y-%m-%dT%H:%M:%S"),
                },
            )

            if created and category:
                post.categories.set([category])

            if featured_image_url:
                filename = os.path.basename(urlparse(featured_image_url).path)
                save_path = f"featured_images/{post.slug}/{filename}"
                new_img_url = download_image(featured_image_url, save_path)
                post.featured_image = save_path

            post.content = updated_content
            post.save()

            # Tags
            tags = get_or_create_tags(post_data["tags"])
            post.tags.set(tags)

        page += 1

    print("Import complete.")
