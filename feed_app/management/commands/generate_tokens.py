from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Generate tokens for users who do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Generate token for specific username'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Generated token for user '{username}': {token.key}")
                    )
                else:
                    self.stdout.write(f"User '{username}' already has token: {token.key}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{username}' does not exist")
                )
        else:
            # Generate tokens for all users
            users = User.objects.all()
            created_count = 0
            
            for user in users:
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    created_count += 1
                    self.stdout.write(f"Generated token for '{user.username}': {token.key}")
            
            self.stdout.write(
                self.style.SUCCESS(f"\nGenerated {created_count} new tokens for {users.count()} users")
            ) 