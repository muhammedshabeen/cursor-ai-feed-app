from django.core.management.base import BaseCommand
from feed_app.models import RelevanceWeight

class Command(BaseCommand):
    help = 'Set up default relevance weights for post scoring'

    def handle(self, *args, **options):
        # Check if default weights already exist
        if RelevanceWeight.objects.filter(is_active=True).exists():
            self.stdout.write("Default weights already exist. Skipping...")
            return

        # Create default weights
        default_weights = RelevanceWeight.objects.create(
            name="Default Weights",
            primary_tag_weight=1.0,
            secondary_tag_weight=0.5,
            freshness_weight=0.3,
            seen_penalty=0.1,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created default relevance weights: {default_weights.name}"
            )
        )
        self.stdout.write(f"  - Primary tag weight: {default_weights.primary_tag_weight}")
        self.stdout.write(f"  - Secondary tag weight: {default_weights.secondary_tag_weight}")
        self.stdout.write(f"  - Freshness weight: {default_weights.freshness_weight}")
        self.stdout.write(f"  - Seen penalty: {default_weights.seen_penalty}") 