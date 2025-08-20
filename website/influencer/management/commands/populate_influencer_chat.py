from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from influencer.models import Influencer, InfluencerCommunityPost
from django.utils import timezone
from datetime import timedelta
import re
import random
import os


class Command(BaseCommand):
    help = "Populate influencer community from structured text file using random real users with realistic timestamps"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the text file containing posts and replies'
        )
        parser.add_argument(
            '--influencer',
            type=str,
            help='Slug of the influencer'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        influencer_identifier = options['influencer']

        if not file_path or not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        if not influencer_identifier:
            self.stdout.write(self.style.ERROR("Please provide influencer slug using --influencer"))
            return

        # Read data from file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()

        # Get influencer
        try:
            influencer = Influencer.objects.get(slug=influencer_identifier)
        except Influencer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Influencer not found: {influencer_identifier}"))
            return

        # Get all real users (non-admin) once
        users = list(User.objects.filter(is_staff=False, is_superuser=False))
        if not users:
            self.stdout.write(self.style.ERROR("No non-admin users found in the database!"))
            return

        entries = data.strip().split('***')
        last_post = None
        total_posts = 0
        total_replies = 0

        # Start time: up to 90 days ago
        current_time = timezone.now() - timedelta(days=random.randint(1, 90))

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Move time forward randomly (1–6 hours for realism)
            current_time += timedelta(hours=random.randint(1, 6), minutes=random.randint(1, 59))

            # Match Post
            post_match = re.match(r'\*\*Post by @[\w_]+:\*\*\s*(.*)', entry, re.DOTALL)
            if post_match:
                content = post_match.group(1)
                user = random.choice(users)
                post = InfluencerCommunityPost.objects.create(
                    influencer=influencer,
                    user=user,
                    content=content.strip(),
                    #created_at=current_time,
                    updated_at=current_time,
                )
                last_post = post
                total_posts += 1
                continue

            # Match Reply
            reply_match = re.match(r'\*\*Reply by @[\w_]+:\*\*\s*(.*)', entry, re.DOTALL)
            if reply_match and last_post:
                content = reply_match.group(1)
                user = random.choice(users)
                InfluencerCommunityPost.objects.create(
                    influencer=influencer,
                    user=user,
                    content=content.strip(),
                    parent=last_post,
                    #created_at=current_time,
                    updated_at=current_time,
                )
                total_replies += 1
                continue

        self.stdout.write(self.style.SUCCESS(
            f"Populated influencer '{influencer}' with {total_posts} posts and {total_replies} replies."
        ))
