# your_app_name/management/commands/populate_categories.py

from django.core.management.base import BaseCommand
from website.influencer.models import Category 

class Command(BaseCommand):
    help = 'Populates the Category model with predefined categories.'

    def handle(self, *args, **kwargs):
        categories_to_add = [
            "Entertainment",
            "Automobile",
            "Technology",
            "Politics",
            "World",
            "Education",
            "Sports",
            "Lifestyle",
            "Trending",
            "Others",
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("Adding Categories..."))

        for category_name in categories_to_add:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added category: '{category.name}'"))
            else:
                self.stdout.write(self.style.WARNING(f"Category '{category.name}' already exists. Skipping."))
        
        self.stdout.write(self.style.SUCCESS("\nCategory population complete."))

