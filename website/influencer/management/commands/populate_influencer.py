# your_app_name/management/commands/populate_influencer.py

from django.core.management.base import BaseCommand, CommandError
from influencer.models import Influencer, InfluencerImage, InfluencerVideo, InfluencerTweet, Category
from django.utils.text import slugify
from django.db import transaction
import yaml
import datetime # Import datetime for handling date objects

class Command(BaseCommand):
    help = 'Populates influencer data from a YAML file.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the YAML file containing influencer data.')

    def handle(self, *args, **options):
        file_path = options['file_path']

        self.stdout.write(f"Attempting to read data from: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, list):
                raise CommandError("YAML file must contain a list of influencer dictionaries.")

            for influencer_data in data:
                name = influencer_data.get('name')
                if not name:
                    self.stdout.write(self.style.ERROR(f"Skipping entry: 'name' is a required field for an influencer."))
                    continue

                self.stdout.write(f"\nProcessing influencer: {name}")

                # Prepare Influencer fields, handling defaults and transformations
                influencer_fields = {k: v for k, v in influencer_data.items() if k not in ['images', 'videos', 'tweets', 'categories']}
                
                # Handle date_of_birth: Check if it's a string that needs parsing, or already a date object
                date_of_birth_value = influencer_fields.get('date_of_birth')
                if isinstance(date_of_birth_value, str):
                    try:
                        influencer_fields['date_of_birth'] = datetime.datetime.strptime(date_of_birth_value, '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"Invalid date format for {name}'s date_of_birth: {date_of_birth_value}. Expected YYYY-MM-DD. Skipping date."))
                        influencer_fields['date_of_birth'] = None
                elif isinstance(date_of_birth_value, datetime.date):
                    # It's already a date object, no conversion needed.
                    # This handles cases where PyYAML automatically parses 'YYYY-MM-DD' into a date object.
                    pass 
                else:
                    # Handle other unexpected types or None values by setting to None
                    influencer_fields['date_of_birth'] = None

                # Pop out age as it's a calculated property, not a stored field
                influencer_fields.pop('age', None)

                # Get or create the Influencer instance.
                # The slug will be handled by the Influencer model's save method.
                try:
                    influencer, created = Influencer.objects.get_or_create(
                        name=name,
                        defaults=influencer_fields
                    )
                    
                    if not created:
                        # If influencer already exists, update its fields based on YAML data
                        # This ensures the YAML is the source of truth for the main profile data
                        for key, value in influencer_fields.items():
                            setattr(influencer, key, value)
                        influencer.save() # Call save to trigger custom save logic (like slug generation/update)
                        self.stdout.write(self.style.WARNING(f"Influencer '{influencer.name}' already exists. Updating existing profile."))
                    else:
                         self.stdout.write(self.style.SUCCESS(f"Successfully created new influencer: '{influencer.name}' (Slug: {influencer.slug})"))


                    # Handle Categories (Many-to-Many field)
                    categories_data = influencer_data.get('categories', [])
                    if categories_data:
                        influencer.categories.clear() # Clear existing categories to sync with YAML
                        for cat_name in categories_data:
                            category, _ = Category.objects.get_or_create(name=cat_name)
                            influencer.categories.add(category)
                        self.stdout.write(f"Updated categories for {influencer.name}: {', '.join(categories_data)}")

                    # Handle Images
                    images_data = influencer_data.get('images', [])
                    for i, image_dict in enumerate(images_data):
                        image_url = image_dict.get('image_url')
                        if image_url:
                            image, image_created = InfluencerImage.objects.get_or_create(
                                influencer=influencer,
                                image_url=image_url,
                                defaults={
                                    'caption': image_dict.get('caption', ''),
                                    'display_order': image_dict.get('display_order', i + 1)
                                }
                            )
                            if image_created:
                                self.stdout.write(self.style.SUCCESS(f"  Added Image: {image_url}"))
                            else:
                                self.stdout.write(self.style.WARNING(f"  Image already exists: {image_url}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  Skipping image entry due to missing 'image_url' for {name}"))

                    # Handle Videos
                    videos_data = influencer_data.get('videos', [])
                    for i, video_dict in enumerate(videos_data):
                        video_url = video_dict.get('video_url')
                        if video_url:
                            source = video_dict.get('source', '')
                            # Attempt to infer source if not provided, but prioritize YAML 'source'
                            if not source:
                                if 'youtube.com' in video_url or 'youtu.be' in video_url:
                                    source = 'youtube'
                                elif 'instagram.com' in video_url:
                                    source = 'instagram'
                                elif 'tiktok.com' in video_url:
                                    source = 'tiktok'
                            
                            if source: # Only add if source could be determined
                                video, video_created = InfluencerVideo.objects.get_or_create(
                                    influencer=influencer,
                                    video_url=video_url,
                                    defaults={
                                        'source': source,
                                        'caption': video_dict.get('caption', ''),
                                        'display_order': video_dict.get('display_order', i + 1)
                                    }
                                )
                                if video_created:
                                    self.stdout.write(self.style.SUCCESS(f"  Added Video ({source}): {video_url}"))
                                else:
                                    self.stdout.write(self.style.WARNING(f"  Video already exists ({source}): {video_url}"))
                            else:
                                self.stdout.write(self.style.ERROR(f"  Skipping video entry for {name}: Could not determine source for URL {video_url}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  Skipping video entry due to missing 'video_url' for {name}"))

                    # Handle Tweets
                    tweets_data = influencer_data.get('tweets', [])
                    for i, tweet_dict in enumerate(tweets_data):
                        tweet_url = tweet_dict.get('tweet_url')
                        if tweet_url:
                            tweet, tweet_created = InfluencerTweet.objects.get_or_create(
                                influencer=influencer,
                                tweet_url=tweet_url,
                                defaults={
                                    'caption': tweet_dict.get('caption', ''),
                                    'display_order': tweet_dict.get('display_order', i + 1)
                                }
                            )
                            if tweet_created:
                                self.stdout.write(self.style.SUCCESS(f"  Added Tweet: {tweet_url}"))
                            else:
                                self.stdout.write(self.style.WARNING(f"  Tweet already exists: {tweet_url}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  Skipping tweet entry due to missing 'tweet_url' for {name}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing influencer '{name}': {e}"))
                    # If an error occurs during an influencer's processing, we don't halt the entire command,
                    # but rather log it and continue with the next influencer if possible.

            self.stdout.write(self.style.SUCCESS("\n--- Data population completed ---"))

        except FileNotFoundError:
            raise CommandError(f"YAML file not found at '{file_path}'")
        except yaml.YAMLError as e:
            raise CommandError(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred: {e}")

