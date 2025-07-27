from django.core.management.base import BaseCommand
from blog.models import Post

class Command(BaseCommand):
    help = 'Update meta_description, featured_image_alt, and meta_keywords in existing posts'

    def handle(self, *args, **kwargs):
        stop_words = {'the', 'and', 'in', 'on', 'of', 'a', 'an', 'to', 'for', 'with', 'by'}

        def extract_keywords(title):
            words = [word.strip(".,!?").lower() for word in title.split()]
            keywords = [word for word in words if word and word not in stop_words]
            return ', '.join(keywords[:8])

        updated_count = 0

        for post in Post.objects.all():
            updated = False

            if not post.meta_description:
                post.meta_description = post.title
                updated = True

            if not post.featured_image_alt:
                post.featured_image_alt = post.title
                updated = True

            if not post.meta_keywords:
                post.meta_keywords = extract_keywords(post.title)
                updated = True

            if updated:
                post.save(update_fields=['meta_description', 'featured_image_alt', 'meta_keywords'])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} post(s) successfully.'))
