# your_app_name/management/commands/fetch_influencer_data.py

import io
import os
import re
import sys
import traceback
from datetime import datetime
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from influencer.models import (
    Influencer,
    InfluencerImage,
    InfluencerVideo,
    InfluencerTweet,
)

# ---- Instagram (instaloader) ----
try:
    import instaloader
except Exception:
    instaloader = None

# ---- YouTube (yt-dlp) ----
try:
    import yt_dlp
except Exception:
    yt_dlp = None

# ---- Twitter/X (snscrape) ----
try:
    import snscrape.modules.twitter as sntwitter
except Exception:
    sntwitter = None


def clean_handle(value: str) -> str:
    if not value:
        return ""
    v = value.strip()
    v = v.lstrip("@")
    return v


def unique_add(model, **kwargs):
    """Create if not exists by a natural key (URL), otherwise do nothing."""
    url_field = None
    for k in ("image_url", "video_url", "tweet_url"):
        if k in kwargs:
            url_field = k
            break
    if not url_field:
        return model.objects.create(**kwargs)

    existing = model.objects.filter(**{url_field: kwargs[url_field]}).first()
    if existing:
        # Update FK if needed (e.g., moved to different influencer)
        changed = False
        for k, v in kwargs.items():
            if getattr(existing, k) != v:
                setattr(existing, k, v)
                changed = True
        if changed:
            existing.save()
        return existing
    return model.objects.create(**kwargs)


def download_to_imagefield(instance, field_name, url, default_name):
    """Download a remote image URL into an ImageField of instance."""
    if not url:
        return False
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        # Infer extension
        ext = None
        ct = r.headers.get("Content-Type", "")
        if "jpeg" in ct or "jpg" in ct:
            ext = "jpg"
        elif "png" in ct:
            ext = "png"
        elif "webp" in ct:
            ext = "webp"
        else:
            # Fallback from URL path
            path = urlparse(url).path
            m = re.search(r"\.(jpg|jpeg|png|webp)(?:\?|$)", path, re.IGNORECASE)
            ext = (m.group(1).lower() if m else "jpg")

        slug = getattr(instance, "slug", "") or slugify(getattr(instance, "name", "image"))
        filename = f"{slug}-{default_name}.{ext}"
        getattr(instance, field_name).save(filename, ContentFile(r.content), save=False)
        return True
    except Exception:
        return False


# -------------------------
# Instagram scraping
# -------------------------
def fetch_instagram(influencer: Influencer, max_posts=6):
    if not instaloader:
        print("instaloader is not installed; skipping Instagram.")
        return

    username = clean_handle(influencer.instagram_handle)
    if not username:
        return

    L = instaloader.Instaloader(download_pictures=False, download_videos=False, quiet=True)
    # No login: you can still fetch public profiles; login improves reliability
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        print(f"[Instagram] Failed to load profile '{username}': {e}")
        return

    # Meta
    try:
        if not influencer.full_name:
            influencer.full_name = profile.full_name or influencer.full_name
        if not influencer.biography:
            influencer.biography = profile.biography or influencer.biography
        if profile.followers and not influencer.instagram_followers:
            influencer.instagram_followers = profile.followers
    except Exception:
        pass

    # Profile pic -> profile_pic/poster_pic
    try:
        pic_url = str(profile.profile_pic_url)
        if pic_url:
            # Ensure slug exists to use slug-based upload_to names
            if not influencer.slug:
                influencer.slug = slugify(influencer.name)
            # Download profile pic to both fields if empty
            if not influencer.profile_pic:
                download_to_imagefield(influencer, "profile_pic", pic_url, "profile")
            if not influencer.poster_pic:
                download_to_imagefield(influencer, "poster_pic", pic_url, "poster")
    except Exception:
        pass

    influencer.save()

    # Recent media → InfluencerImage / InfluencerVideo
    try:
        count = 0
        for post in profile.get_posts():
            if count >= max_posts:
                break
            # post.url is usually an image thumbnail URL; post.is_video flag available
            # For reels/videos, prefer post.video_url if available (may require login).
            caption = (post.caption or "").strip()[:250] or None
            if post.is_video:
                # Use post.url (thumbnail) OR shortcode URL as fallback
                shortcode = getattr(post, "shortcode", "")
                page_url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else post.url
                unique_add(
                    InfluencerVideo,
                    influencer=influencer,
                    source="instagram",
                    video_url=page_url,
                    caption=caption,
                    display_order=count,
                )
            else:
                unique_add(
                    InfluencerImage,
                    influencer=influencer,
                    image_url=post.url,
                    caption=caption,
                    display_order=count,
                )
            count += 1
    except Exception as e:
        print(f"[Instagram] Error fetching posts for {username}: {e}")


# -------------------------
# YouTube scraping
# -------------------------
def normalize_youtube_channel(value: str) -> str:
    """
    Accepts:
      - Full channel URL: https://www.youtube.com/channel/UCxxxx
      - Handle URL: https://www.youtube.com/@handle
      - Handle only: @handle
      - Custom URL: https://www.youtube.com/c/CustomName
    Returns a URL suitable for yt-dlp.
    """
    if not value:
        return ""
    v = value.strip()
    if not v.startswith("http"):
        # Assume handle
        if not v.startswith("@"):
            v = "@" + v
        return f"https://www.youtube.com/{v}"
    return v


def fetch_youtube(influencer: Influencer, max_videos=6):
    if not yt_dlp:
        print("yt-dlp is not installed; skipping YouTube.")
        return
    channel_spec = normalize_youtube_channel(influencer.youtube_channel)
    if not channel_spec:
        return

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_spec, download=False)
    except Exception as e:
        print(f"[YouTube] Failed to extract channel: {e}")
        return

    # info can be a channel page with entries (videos) or a redirect
    videos = []
    try:
        if "entries" in info and info["entries"]:
            # Some channel pages return sections; try to flatten video entries
            for ent in info["entries"]:
                if ent and ent.get("_type") == "url" and "watch" in ent.get("url", ""):
                    videos.append(ent)
                # sometimes entries are playlists/sections that contain their own entries
                if ent and "entries" in ent:
                    for sub in ent["entries"] or []:
                        if sub and sub.get("_type") == "url" and "watch" in sub.get("url", ""):
                            videos.append(sub)
        # If still empty, try channel /videos URL
        if not videos and info.get("webpage_url"):
            alt = info["webpage_url"].rstrip("/") + "/videos"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                alt_info = ydl.extract_info(alt, download=False)
                for ent in alt_info.get("entries", []) or []:
                    if ent and ent.get("_type") == "url" and "watch" in ent.get("url", ""):
                        videos.append(ent)
    except Exception:
        pass

    # Save first N videos
    added = 0
    for v in videos:
        if added >= max_videos:
            break
        title = (v.get("title") or "").strip()
        url = v.get("url") or v.get("webpage_url")
        if not url:
            continue
        if not url.startswith("http"):
            url = "https://www.youtube.com" + url
        unique_add(
            InfluencerVideo,
            influencer=influencer,
            source="youtube",
            video_url=url,
            caption=title[:250] or None,
            display_order=added,
        )
        added += 1


# -------------------------
# Twitter/X scraping
# -------------------------
def fetch_twitter(influencer: Influencer, max_tweets=6):
    if not sntwitter:
        print("snscrape is not installed; skipping Twitter.")
        return
    handle = clean_handle(influencer.twitter_handle)
    if not handle:
        return
    try:
        scraper = sntwitter.TwitterUserScraper(handle)
        count = 0
        for tweet in scraper.get_items():
            if count >= max_tweets:
                break
            url = f"https://twitter.com/{handle}/status/{tweet.id}"
            text = tweet.rawContent[:250] if getattr(tweet, "rawContent", None) else None
            unique_add(
                InfluencerTweet,
                influencer=influencer,
                tweet_url=url,
                caption=text,
                display_order=count,
            )
            count += 1
    except Exception as e:
        print(f"[Twitter] Error scraping @{handle}: {e}")


class Command(BaseCommand):
    help = "Auto-fill influencer data by scraping Instagram, YouTube, and Twitter/X."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            help="Slug of an existing Influencer to update (recommended).",
        )
        parser.add_argument(
            "--name",
            help="Create or update Influencer by name (will create if not exists).",
        )
        parser.add_argument("--ig", dest="instagram_handle", help="Instagram handle (with or without @)")
        parser.add_argument("--yt", dest="youtube_channel", help="YouTube channel URL or @handle")
        parser.add_argument("--tw", dest="twitter_handle", help="Twitter/X handle (with or without @)")
        parser.add_argument("--max-ig-posts", type=int, default=6)
        parser.add_argument("--max-yt-videos", type=int, default=6)
        parser.add_argument("--max-tweets", type=int, default=6)

    @transaction.atomic
    def handle(self, *args, **opts):
        slug = opts.get("slug")
        name = opts.get("name")
        ig = opts.get("instagram_handle")
        yt = opts.get("youtube_channel")
        tw = opts.get("twitter_handle")
        max_ig = opts.get("max_ig_posts") or 6
        max_yt = opts.get("max_yt_videos") or 6
        max_tw = opts.get("max_tweets") or 6

        if not any([slug, name]):
            raise CommandError("Provide --slug of an existing Influencer OR --name to create one.")

        if slug:
            inf = Influencer.objects.filter(slug=slug).first()
            if not inf:
                raise CommandError(f"No Influencer found with slug '{slug}'.")
        else:
            # Create or fetch by name
            inf, _created = Influencer.objects.get_or_create(name=name)
            if not inf.slug:
                # Generate unique slug like your model does
                base_slug = slugify(inf.name)
                unique_slug = base_slug
                num = 1
                while Influencer.objects.filter(slug=unique_slug).exclude(pk=inf.pk).exists():
                    unique_slug = f"{base_slug}-{num}"
                    num += 1
                inf.slug = unique_slug

        # Update handles if provided
        if ig:
            inf.instagram_handle = clean_handle(ig)
        if yt:
            inf.youtube_channel = yt.strip()
        if tw:
            inf.twitter_handle = clean_handle(tw)

        # Initial save to ensure slug exists for file naming
        inf.save()

        # Fetch per platform
        try:
            fetch_instagram(inf, max_posts=max_ig)
        except Exception:
            traceback.print_exc()

        try:
            fetch_youtube(inf, max_videos=max_yt)
        except Exception:
            traceback.print_exc()

        try:
            fetch_twitter(inf, max_tweets=max_tw)
        except Exception:
            traceback.print_exc()

        # Final save
        inf.save()

        self.stdout.write(self.style.SUCCESS(f"Scrape completed for Influencer: {inf.name} ({inf.slug})"))
