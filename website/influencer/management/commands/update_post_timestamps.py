from django.core.management.base import BaseCommand
from influencer.models import Influencer, InfluencerCommunityPost
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = "Update community post timestamps for a specific influencer (realistic spread with cascading replies)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--influencer",
            type=str,
            required=True,
            help="Slug of the influencer whose community posts should be updated"
        )

    def handle(self, *args, **options):
        slug = options["influencer"]

        try:
            influencer = Influencer.objects.get(slug=slug)
        except Influencer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Influencer not found: {slug}"))
            return

        posts = influencer.community_posts.all()
        if not posts.exists():
            self.stdout.write(self.style.WARNING(f"No posts found for influencer: {slug}"))
            return

        base_time = timezone.now() - timedelta(days=90)

        # Helper to recursively update replies
        def update_replies(post, parent_time):
            replies = post.replies.all().order_by("id")
            day_e = 89
            
            for reply in replies:
                day_s = day_e - 4
                random_days = random.randint(day_s, day_e)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                parent_time = base_time + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
                day_e = day_e -5 
                print(f"reply: {reply.id}")
                # Reply time: always after parent
                random_minutes = random.randint(5, 360)  # 5 min – 6 hours
                reply_time = parent_time + timedelta(minutes=random_minutes)

                if reply_time > timezone.now():
                    reply_time = timezone.now() - timedelta(minutes=random.randint(1, 60))

                #reply.created_at = reply_time
                reply.updated_at = reply_time
                reply.save(update_fields=["updated_at"])
                print(f"reply_time: {reply_time}")

                # Recurse for replies to this reply
                update_replies(reply, reply_time)

        # Update top-level posts and then cascade replies
        for post in posts.filter(parent__isnull=True).order_by("id"):
            print(f"post: {post.id}")
            random_days = random.randint(0, 90)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            post_time = base_time + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

            if post_time > timezone.now():
                post_time = timezone.now() - timedelta(minutes=random.randint(1, 60))

            #post.created_at = post_time
            post.updated_at = post_time
            post.save(update_fields=["updated_at"])
            print(f"post_time: {post_time}")

            # Cascade to replies
            update_replies(post, post_time)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {posts.count()} posts (including nested replies) for influencer '{influencer.name}' ({slug})"
            )
        )
