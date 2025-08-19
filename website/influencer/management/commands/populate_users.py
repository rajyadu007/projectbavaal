# management/commands/populate_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from faker import Faker
from faker.providers import person
import random
import requests
from io import BytesIO
from PIL import Image
import os

# Import your UserProfile model
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Populate database with fake users with country-specific names and profile pictures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--country',
            type=str,
            default='india',
            choices=['india', 'us', 'uk', 'germany', 'france', 'japan', 'china', 'brazil', 'mexico', 'russia'],
            help='Country for name generation (india, us, uk, germany, france, japan, china, brazil, mexico, russia)'
        )

    def get_faker_for_country(self, country):
        """Get Faker instance with appropriate locale for the country"""
        country_locales = {
            'india': 'en_IN',      # Indian English
            'us': 'en_US',         # United States
            'uk': 'en_GB',         # United Kingdom
            'germany': 'de_DE',    # Germany
            'france': 'fr_FR',     # France
            'japan': 'ja_JP',      # Japan
            'china': 'zh_CN',      # China
            'brazil': 'pt_BR',     # Brazil
            'mexico': 'es_MX',     # Mexico
            'russia': 'ru_RU',     # Russia
        }
        
        locale = country_locales.get(country.lower(), 'en_US')
        try:
            return Faker(locale)
        except:
            # Fallback to English if locale not available
            return Faker('en_US')

    def generate_fake_image(self, first_name, email, width=200, height=200):
        """Generate a simple colored image with the user's initial"""
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        try:
            # Create a random background color
            bg_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            
            # Create image
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to use a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Add user initial
            initial = first_name[0].upper() if first_name else email[0].upper()
            
            # Calculate text position (center)
            try:
                # For newer PIL versions
                bbox = draw.textbbox((0, 0), initial, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # For older PIL versions
                text_width, text_height = draw.textsize(initial, font=font)
            
            position = ((width - text_width) // 2, (height - text_height) // 2)
            draw.text(position, initial, fill=(255, 255, 255), font=font)
            
            # Save to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr, None
        except Exception as e:
            return None, f"Image generation failed: {e}"

    def download_avatar(self, size=200):
        """Download a random avatar from a placeholder service"""
        try:
            response = requests.get(f'https://i.pravatar.cc/{size}?{random.randint(1, 1000)}', timeout=10)
            if response.status_code == 200:
                return BytesIO(response.content), None
            return None, f"HTTP status {response.status_code}"
        except Exception as e:
            return None, f"Download failed: {e}"

    def create_profile_image(self, first_name, email, max_attempts=5):
        """Try to create a profile image with multiple attempts"""
        for attempt in range(1, max_attempts + 1):
            # Try download first, then generation
            if attempt <= 3:  # First 3 attempts: try download
                image_data, error = self.download_avatar()
                method = "download"
            else:  # Remaining attempts: try generation
                image_data, error = self.generate_fake_image(first_name, email)
                method = "generate"
            
            if image_data:
                return image_data, method, attempt
            
            self.stdout.write(self.style.WARNING(f"Attempt {attempt}/{max_attempts} ({method}) failed: {error}"))
            
            # Small delay between attempts
            if attempt < max_attempts:
                import time
                time.sleep(0.3)
        
        return None, None, max_attempts

    def handle(self, *args, **options):
        num_users = options['num_users']
        country = options['country'].lower()
        max_image_attempts = 5
        
        # Get country-specific faker
        fake = self.get_faker_for_country(country)
        
        self.stdout.write(self.style.SUCCESS(f"Creating {num_users} users with {country.upper()} names..."))
        
        users_created = 0
        total_attempts = 0
        
        while users_created < num_users:
            total_attempts += 1
            
            # Generate country-specific name
            if country == 'india':
                # Indian names often have specific patterns
                first_name = fake.first_name()
                last_name = fake.last_name()
                # Indian names might have common surnames
                indian_surnames = ['Singh', 'Kumar', 'Patel', 'Sharma', 'Gupta', 'Khan', 'Verma', 'Reddy', 'Mehta', 'Choudhury', 'Yadav']
                if random.random() > 0.7:  # 30% chance to use Indian surname
                    last_name = random.choice(indian_surnames)
            else:
                first_name = fake.first_name()
                last_name = fake.last_name()
            
            # Generate email based on country
            if country == 'india':
                email_domain = random.choice(['@stackvalue.in'])
            elif country == 'japan':
                email_domain = random.choice(['@stackvalue.jp'])
            elif country == 'china':
                email_domain = random.choice(['@stackvalue.cn'])
            else:
                email_domain = '@example.com'
            
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{base_email}{email_domain}"
            
            # Ensure email is unique
            counter = 1
            original_email = email
            while User.objects.filter(email=email).exists():
                email = f"{base_email}{counter}{email_domain}"
                counter += 1
            
            self.stdout.write(f"Creating: {first_name} {last_name} ({email})")
            
            # Try to create profile image first
            image_data, method, attempts_used = self.create_profile_image(first_name, email, max_image_attempts)
            
            if not image_data:
                self.stdout.write(self.style.WARNING(f"⚠️  Skipping {first_name} {last_name} - image creation failed"))
                continue
            
            # If image created successfully, now create the user
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='!@#$qwertyu',
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create UserProfile and assign the image
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Save the successfully created image
                filename = f"profile_{user.id}.png"
                profile.profile_picture.save(filename, ContentFile(image_data.getvalue()), save=False)
                profile.save()
                
                users_created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created user {users_created}/{num_users}: {first_name} {last_name}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to create user: {e}"))
                continue
        
        # Final statistics
        total_users = User.objects.count()
        users_with_images = UserProfile.objects.exclude(profile_picture='').count()
        
        self.stdout.write(self.style.SUCCESS(f"\n=== {country.upper()} USERS CREATED ==="))
        self.stdout.write(self.style.SUCCESS(f"Requested: {num_users}"))
        self.stdout.write(self.style.SUCCESS(f"Created: {users_created}"))
        self.stdout.write(self.style.SUCCESS(f"Success rate: {(users_created/num_users*100):.1f}%"))
        
        # Show sample of created users
        sample_users = User.objects.select_related('userprofile').order_by('-id')[:5]
        if sample_users:
            self.stdout.write(self.style.SUCCESS(f"\nSample {country} users:"))
            for user in sample_users:
                self.stdout.write(f"  {user.first_name} {user.last_name} - {user.email} ✅")

# Additional function to create mixed country users
def create_mixed_country_users(num_users_per_country=5):
    """Create users from multiple countries"""
    countries = ['india', 'us', 'uk', 'germany', 'japan', 'china']
    
    for country in countries:
        # You can call the command programmatically or run separately
        print(f"Creating {num_users_per_country} {country} users...")
        # This would require additional setup to call the command internally