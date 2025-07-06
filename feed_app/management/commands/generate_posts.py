import os
import random
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from feed_app.models import Post, Interest
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate random posts with images from Unsplash and random text'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=150,
            help='Number of posts to generate (default: 150)'
        )
        parser.add_argument(
            '--unsplash-key',
            type=str,
            help='Unsplash API key (optional, will use Lorem Picsum if not provided)'
        )

    def handle(self, *args, **options):
        count = options['count']
        unsplash_key = options['unsplash_key']
        
        # Sample text content for posts
        sample_texts = [
            "Just discovered this amazing place! The vibes here are incredible. 🌟",
            "Sometimes you need to take a step back and appreciate the little things in life.",
            "Adventure awaits around every corner. Never stop exploring! 🗺️",
            "Life is what happens when you're busy making other plans.",
            "The best way to predict the future is to create it.",
            "Every moment is a fresh beginning. Embrace the journey! ✨",
            "Nature has a way of healing everything. Take time to connect with it.",
            "Dream big, work hard, stay focused. Success will follow.",
            "The world is full of magic things, patiently waiting for our senses to grow sharper.",
            "Sometimes the most beautiful things in life are the simplest ones.",
            "Life is a journey, not a destination. Enjoy the ride! 🚀",
            "The only way to do great work is to love what you do.",
            "Every day is a new opportunity to be better than yesterday.",
            "The future belongs to those who believe in the beauty of their dreams.",
            "Life is too short to waste time on things that don't matter.",
            "Sometimes you have to go through the worst to get to the best.",
            "The best is yet to come. Keep pushing forward! 💪",
            "Life is beautiful when you choose to see it that way.",
            "Every experience, good or bad, makes you stronger.",
            "The journey of a thousand miles begins with one step.",
            "Don't wait for the perfect moment, take the moment and make it perfect.",
            "Life is not about waiting for the storm to pass, but learning to dance in the rain.",
            "The only limit to your impact is your imagination and commitment.",
            "Every day brings new possibilities. Stay open to them! 🌈",
            "The best way to find yourself is to lose yourself in the service of others.",
            "Life is a beautiful adventure. Make it count! 🎯",
            "Sometimes the smallest things take up the most room in your heart.",
            "The world is your oyster. Go out and find your pearls! 🦪",
            "Every moment spent planning is a moment spent living.",
            "Life is like a camera. Focus on what's important, capture the good times.",
            "The best things in life are free: love, laughter, and memories.",
            "Don't count the days, make the days count! 📅",
            "Life is a gift, and it offers us the privilege, opportunity, and responsibility to give something back.",
            "The only impossible journey is the one you never begin.",
            "Every day is a chance to be better than yesterday.",
            "Life is what you make it. Choose wisely! 🎨",
            "The best way to predict the future is to invent it.",
            "Sometimes you need to lose yourself to find yourself.",
            "Life is a beautiful struggle. Embrace it! 💫",
            "The only way to achieve the impossible is to believe it is possible.",
            "Every experience is a teacher. Learn from everything.",
            "Life is not about finding yourself, it's about creating yourself.",
            "The best time to plant a tree was 20 years ago. The second best time is now.",
            "Sometimes the most important thing in a whole day is the rest we take between two deep breaths.",
            "Life is a series of natural and spontaneous changes. Don't resist them.",
            "The only person you are destined to become is the person you decide to be.",
            "Every day is a new beginning. Take a deep breath and start again.",
            "Life is like riding a bicycle. To keep your balance, you must keep moving.",
            "The best way to find out if you can trust somebody is to trust them.",
            "Sometimes the heart sees what is invisible to the eye.",
            "Life is a journey that must be traveled no matter how bad the roads and accommodations.",
            "The only way to do great work is to love what you do.",
            "Every moment is a fresh beginning. Embrace the journey! ✨",
            "Life is what happens when you're busy making other plans.",
            "The best way to predict the future is to create it.",
            "Sometimes you need to take a step back and appreciate the little things in life.",
            "Adventure awaits around every corner. Never stop exploring! 🗺️",
        ]

        # Get or create some interest tags
        interests = self.get_or_create_interests()
        
        self.stdout.write(f"Generating {count} posts...")
        
        created_count = 0
        for i in range(count):
            try:
                # Generate random text
                text = random.choice(sample_texts)
                
                # Get 1-3 random interests
                num_tags = random.randint(1, 3)
                selected_interests = random.sample(list(interests), min(num_tags, len(interests)))
                
                # Create post without image first
                post = Post.objects.create(text=text)
                post.tags.set(selected_interests)
                
                # Try to fetch and save an image
                if unsplash_key:
                    image_url = self.get_unsplash_image(unsplash_key)
                else:
                    image_url = self.get_lorem_picsum_image()
                
                if image_url:
                    try:
                        response = requests.get(image_url, timeout=10)
                        if response.status_code == 200:
                            # Generate a unique filename
                            filename = f"post_{post.id}_{int(timezone.now().timestamp())}.jpg"
                            post.image.save(filename, ContentFile(response.content), save=True)
                            self.stdout.write(f"✓ Created post {post.id} with image")
                        else:
                            self.stdout.write(f"✓ Created post {post.id} without image (HTTP {response.status_code})")
                    except Exception as e:
                        self.stdout.write(f"✓ Created post {post.id} without image (Error: {str(e)})")
                else:
                    self.stdout.write(f"✓ Created post {post.id} without image")
                
                created_count += 1
                
                # Add some random time variation to posts
                random_hours = random.randint(0, 720)  # Up to 30 days ago
                post.created_at = timezone.now() - timedelta(hours=random_hours)
                post.save()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating post {i+1}: {str(e)}"))
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} posts!")
        )

    def get_or_create_interests(self):
        """Get or create interest tags"""
        interest_names = [
            "Technology", "Travel", "Food", "Music", "Sports", "Art", "Nature", 
            "Fashion", "Photography", "Fitness", "Books", "Movies", "Gaming", 
            "Cooking", "Gardening", "Pets", "Science", "History", "Business", 
            "Education", "Health", "Lifestyle", "Automotive", "Architecture", 
            "Design", "Crafting", "Outdoors", "Fitness", "Wellness", "Adventure",
            "Culture", "Fashion", "Beauty", "Home", "DIY", "Parenting", "Career",
            "Finance", "Politics", "Environment", "Space", "Ocean", "Mountains",
            "Cities", "Countryside", "Beach", "Forest", "Desert", "Winter", "Summer"
        ]
        
        interests = []
        for name in interest_names:
            interest, created = Interest.objects.get_or_create(name=name)
            interests.append(interest)
            if created:
                self.stdout.write(f"Created interest: {name}")
        
        return interests

    def get_unsplash_image(self, api_key):
        """Get a random image from Unsplash"""
        try:
            url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {api_key}"}
            params = {
                "query": random.choice(["nature", "city", "people", "architecture", "food", "travel"]),
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("urls", {}).get("regular")
        except Exception as e:
            self.stdout.write(f"Unsplash API error: {str(e)}")
        
        return None

    def get_lorem_picsum_image(self):
        """Get a random image from Lorem Picsum"""
        try:
            width = random.randint(800, 1200)
            height = random.randint(600, 800)
            return f"https://picsum.photos/{width}/{height}"
        except Exception as e:
            self.stdout.write(f"Lorem Picsum error: {str(e)}")
        
        return None 