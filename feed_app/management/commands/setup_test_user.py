from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from feed_app.models import Interest

class Command(BaseCommand):
    help = 'Set up a test user with specific interests for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for test user (default: testuser)'
        )
        parser.add_argument(
            '--primary-interests',
            type=str,
            default='Technology,Travel,Music',
            help='Comma-separated list of primary interests'
        )
        parser.add_argument(
            '--secondary-interests',
            type=str,
            default='Art,Photography,Fitness',
            help='Comma-separated list of secondary interests'
        )

    def handle(self, *args, **options):
        username = options['username']
        primary_interest_names = [name.strip() for name in options['primary_interests'].split(',')]
        secondary_interest_names = [name.strip() for name in options['secondary_interests'].split(',')]
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(f"Created user: {username}")
        else:
            self.stdout.write(f"Using existing user: {username}")
        
        # Get user profile (should be created automatically by signals)
        try:
            profile = user.profile
        except:
            self.stdout.write(self.style.ERROR(f"User profile not found for {username}"))
            return
        
        # Get or create interests
        primary_interests = []
        for name in primary_interest_names:
            interest, created = Interest.objects.get_or_create(name=name)
            primary_interests.append(interest)
            if created:
                self.stdout.write(f"Created interest: {name}")
        
        secondary_interests = []
        for name in secondary_interest_names:
            interest, created = Interest.objects.get_or_create(name=name)
            secondary_interests.append(interest)
            if created:
                self.stdout.write(f"Created interest: {name}")
        
        # Set interests on profile
        profile.primary_interests.set(primary_interests)
        profile.secondary_interests.set(secondary_interests)
        
        self.stdout.write(f"\nUser {username} configured with:")
        self.stdout.write(f"Primary interests: {', '.join([i.name for i in primary_interests])}")
        self.stdout.write(f"Secondary interests: {', '.join([i.name for i in secondary_interests])}")
        
        self.stdout.write(
            self.style.SUCCESS(f"\nTest user setup complete! You can now run:")
        )
        self.stdout.write(f"python manage.py test_scoring --user-id {user.id}") 