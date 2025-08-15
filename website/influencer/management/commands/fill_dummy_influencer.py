# influencers/management/commands/fill_dummy_influencer.py
import uuid
import random
import yaml
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from influencer.models import Influencer, InfluencerImage, InfluencerVideo, InfluencerTweet


fake = Faker()

class Command(BaseCommand):
    help = "Create influencer data from YAML file or random fake data"

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', nargs='?', type=str, default=None, help='Path to YAML file')

    def handle(self, *args, **options):
        yaml_file = options.get('yaml_file')

        if yaml_file:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            self.stdout.write(self.style.ERROR("No YAML file provided"))
            return

        name = data.get('name') or fake.name()
        slug = data.get('slug') or slugify(name)

        # Delete old with same slug
        Influencer.objects.filter(slug=slug).delete()

        influencer = Influencer.objects.create(
            name=name,
            slug=slug,
            uuid=uuid.uuid4(),
            profile_pic=data.get('profile_pic'),
            poster_pic=data.get('poster_pic'),
            full_name=data.get('full_name'),
            nickname=data.get('nickname'),
            date_of_birth=data.get('date_of_birth'),
            place_of_birth=data.get('place_of_birth'),
            age=data.get('age'),
            height_cm=data.get('height_cm'),
            hair_color=data.get('hair_color'),
            eye_color=data.get('eye_color'),
            education=data.get('education'),
            profession=data.get('profession'),
            biography=data.get('biography'),
            profile_summary=data.get('profile_summary'),
            instagram_handle=data.get('instagram_handle'),
            instagram_followers=data.get('instagram_followers'),
            youtube_channel=data.get('youtube_channel'),
            tiktok_handle=data.get('tiktok_handle'),
            twitter_handle=data.get('twitter_handle'),
            brand_collaborations=data.get('brand_collaborations'),
            media_appearances=data.get('media_appearances'),
            businesses=data.get('businesses'),
            hobbies=data.get('hobbies'),
            estimated_net_worth=data.get('estimated_net_worth'),
            assets=data.get('assets'),
            achievements=data.get('achievements'),
            public_perception=data.get('public_perception'),
            controversies=data.get('controversies'),
        )

        for i, img in enumerate(data.get('images', [])):
            InfluencerImage.objects.create(
                influencer=influencer,
                image_url=img.get('image_url'),
                caption=img.get('caption'),
                display_order=i
            )

        for i, vid in enumerate(data.get('videos', [])):
            InfluencerVideo.objects.create(
                influencer=influencer,
                source=vid.get('source'),
                video_url=vid.get('video_url'),
                caption=vid.get('caption'),
                display_order=i
            )

        for i, tw in enumerate(data.get('tweets', [])):
            InfluencerTweet.objects.create(
                influencer=influencer,
                tweet_url=tw.get('tweet_url'),
                caption=tw.get('caption'),
                display_order=i
            )

        self.stdout.write(self.style.SUCCESS(f"Influencer '{name}' created from {yaml_file}"))
