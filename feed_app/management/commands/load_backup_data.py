from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Loads data from db_backup.json if no users exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.exists():
            self.stdout.write("📦 Loading data from db_backup.json...")
            call_command('loaddata', 'db_backup.json')
            self.stdout.write(self.style.SUCCESS("✅ Data loaded!"))
        else:
            self.stdout.write("ℹ️ Users exist. Skipping data load.")
