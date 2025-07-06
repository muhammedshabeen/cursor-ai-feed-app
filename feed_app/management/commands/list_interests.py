from django.core.management.base import BaseCommand
from feed_app.models import Interest

class Command(BaseCommand):
    help = 'List all available interests with their IDs'

    def handle(self, *args, **options):
        interests = Interest.objects.all().order_by('name')
        
        if not interests:
            self.stdout.write(self.style.WARNING("No interests found. Run 'python manage.py generate_posts' first to create interests."))
            return
        
        self.stdout.write("Available Interests:")
        self.stdout.write("-" * 50)
        
        for interest in interests:
            self.stdout.write(f"ID: {interest.id:2d} | {interest.name}")
        
        self.stdout.write(f"\nTotal: {interests.count()} interests")
        self.stdout.write(self.style.SUCCESS("\nYou can use these IDs in the registration API.")) 