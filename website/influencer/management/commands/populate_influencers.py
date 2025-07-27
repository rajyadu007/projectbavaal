# your_app_name/management/commands/populate_influencers.py

import json
import os
import urllib.request
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from influencer.models import Influencer, Category, Content, Collaboration # Replace 'your_app_name'

class Command(BaseCommand):
    help = 'Populates the Influencer, Content, and Collaboration models from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='The path to the JSON file containing influencer data.',
            default='influencer_data.json', # Default to a file in the project root
            nargs='?' # Make it optional
        )

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        # Construct absolute path to the JSON file
        # Assumes json_file is in the project root (where manage.py is)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_json_path = os.path.join(project_root, json_file_path)

        if not os.path.exists(full_json_path):
            raise CommandError(f"JSON file not found at: {full_json_path}")

        self.stdout.write(self.style.MIGRATE_HEADING(f"Loading data from {json_file_path}..."))

        try:
            with open(full_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise CommandError(f"Invalid JSON format in {json_file_path}")
        except Exception as e:
            raise CommandError(f"Error reading file {json_file_path}: {e}")

        self.stdout.write(self.style.MIGRATE_HEADING("Populating Influencer Data..."))

        for influencer_data in data:
            with transaction.atomic(): # Use atomic transaction for data integrity
                name = influencer_data.get('name')
                if not name:
                    self.stdout.write(self.style.ERROR("Skipping influencer: 'name' is required."))
                    continue

                self.stdout.write(self.style.MIGRATE_HEADING(f"Processing Influencer: {name}"))

                # Create or get Influencer
                influencer, created = Influencer.objects.get_or_create(
                    unique_id=influencer_data.get('unique_id', None), # Use unique_id for get_or_create if available
                    defaults={
                        'name': name,
                        'bio': influencer_data.get('bio', ''),
                        'type': influencer_data.get('type', 'MICRO'),
                        'followers_count': influencer_data.get('followers_count', 0),
                        'likes_count': influencer_data.get('likes_count', 0),
                        'views_count': influencer_data.get('views_count', 0),
                        'posts_count': influencer_data.get('posts_count', 0),
                        'rating': influencer_data.get('rating', 0.0),
                        'collaborations_count': influencer_data.get('collaborations_count', 0),
                        'instagram_url': influencer_data.get('instagram_url', ''),
                        'tiktok_url': influencer_data.get('tiktok_url', ''),
                        'youtube_url': influencer_data.get('youtube_url', ''),
                        'twitter_url': influencer_data.get('twitter_url', ''),
                        'blog_content': influencer_data.get('blog_content', ''),
                    }
                )

                if not created:
                    self.stdout.write(self.style.WARNING(f"Influencer '{name}' already exists. Updating fields."))
                    # Update fields if influencer already exists
                    for key, value in influencer_data.items():
                        if key not in ['unique_id', 'contents', 'collaborations', 'categories', 'profile_image_url']:
                            setattr(influencer, key, value)
                    influencer.save() # Save updated fields

                # Handle profile image download and save
                profile_image_url = influencer_data.get('profile_image_url')
                if profile_image_url and not influencer.profile_image: # Only download if no image exists
                    try:
                        result = urllib.request.urlretrieve(profile_image_url)
                        influencer.profile_image.save(
                            os.path.basename(profile_image_url.split('?')[0]), # Get filename, remove query params
                            File(open(result[0], 'rb'))
                        )
                        influencer.save()
                        self.stdout.write(self.style.SUCCESS(f"  Downloaded profile image for {name}."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Failed to download profile image for {name}: {e}"))

                # Handle Categories (Many-to-Many)
                categories_data = influencer_data.get('categories', [])
                influencer.categories.clear() # Clear existing categories before adding
                for cat_name in categories_data:
                    category, cat_created = Category.objects.get_or_create(name=cat_name)
                    influencer.categories.add(category)
                    if cat_created:
                        self.stdout.write(self.style.SUCCESS(f"  Added new category: '{cat_name}'"))
                self.stdout.write(self.style.SUCCESS(f"  Categories updated for {name}."))

                # Handle Contents (related objects)
                contents_data = influencer_data.get('contents', [])
                # Delete existing content for this influencer to prevent duplicates on re-run
                influencer.contents.all().delete()
                for content_data in contents_data:
                    content_title = content_data.get('title')
                    if not content_title:
                        self.stdout.write(self.style.WARNING(f"  Skipping content for {name}: 'title' is required."))
                        continue

                    content = Content.objects.create(
                        influencer=influencer,
                        title=content_title,
                        external_url=content_data.get('external_url', ''),
                        views_count=content_data.get('views_count', 0),
                        likes_count=content_data.get('likes_count', 0),
                        content_type=content_data.get('content_type', 'VIDEO'),
                        published_date=content_data.get('published_date', None)
                    )
                    # Handle content thumbnail download and save
                    thumbnail_url = content_data.get('thumbnail_url')
                    if thumbnail_url:
                        try:
                            result = urllib.request.urlretrieve(thumbnail_url)
                            content.thumbnail.save(
                                os.path.basename(thumbnail_url.split('?')[0]), # Get filename, remove query params
                                File(open(result[0], 'rb'))
                            )
                            content.save()
                            self.stdout.write(self.style.SUCCESS(f"    Downloaded thumbnail for content '{content_title}'."))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"    Failed to download thumbnail for content '{content_title}': {e}"))
                    self.stdout.write(self.style.SUCCESS(f"  Added content: '{content_title}'"))

                # Handle Collaborations (related objects)
                collaborations_data = influencer_data.get('collaborations', [])
                # Delete existing collaborations for this influencer to prevent duplicates on re-run
                influencer.collaborations.all().delete()
                for collab_data in collaborations_data:
                    campaign_name = collab_data.get('campaign_name')
                    if not campaign_name:
                        self.stdout.write(self.style.WARNING(f"  Skipping collaboration for {name}: 'campaign_name' is required."))
                        continue

                    collab = Collaboration.objects.create(
                        influencer=influencer,
                        campaign_name=campaign_name,
                        external_url=collab_data.get('external_url', ''),
                        engagement_metric=collab_data.get('engagement_metric', ''),
                        start_date=collab_data.get('start_date', None),
                        end_date=collab_data.get('end_date', None),
                        is_sponsored=collab_data.get('is_sponsored', True)
                    )
                    # Handle collaboration thumbnail download and save
                    thumbnail_url = collab_data.get('thumbnail_url')
                    if thumbnail_url:
                        try:
                            result = urllib.request.urlretrieve(thumbnail_url)
                            collab.thumbnail.save(
                                os.path.basename(thumbnail_url.split('?')[0]), # Get filename, remove query params
                                File(open(result[0], 'rb'))
                            )
                            collab.save()
                            self.stdout.write(self.style.SUCCESS(f"    Downloaded thumbnail for collaboration '{campaign_name}'."))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"    Failed to download thumbnail for collaboration '{campaign_name}': {e}"))
                    self.stdout.write(self.style.SUCCESS(f"  Added collaboration: '{campaign_name}'"))

                self.stdout.write(self.style.SUCCESS(f"Influencer '{name}' processed successfully.\n"))
        
        self.stdout.write(self.style.SUCCESS("Influencer data population complete."))

