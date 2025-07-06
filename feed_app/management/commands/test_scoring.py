from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from feed_app.models import Post, Interest, RelevanceWeight
from feed_app.utils import calculate_post_score, get_user_feed

class Command(BaseCommand):
    help = 'Test the post scoring algorithm with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Test scoring for specific user ID'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        # Get or create a test user
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} does not exist"))
                return
        else:
            # Create a test user if none specified
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            if created:
                self.stdout.write(f"Created test user: {user.username}")
        
        # Get active weights
        try:
            weights = RelevanceWeight.objects.filter(is_active=True).first()
            if weights:
                self.stdout.write(f"Using weights: {weights.name}")
            else:
                self.stdout.write("No active weights found, using defaults")
                weights = None
        except Exception as e:
            self.stdout.write(f"Error getting weights: {e}")
            weights = None
        
        # Get some sample posts
        posts = Post.objects.all()[:10]
        
        if not posts:
            self.stdout.write(self.style.ERROR("No posts found. Run 'python manage.py generate_posts' first."))
            return
        
        self.stdout.write(f"\nTesting scoring for user: {user.username}")
        self.stdout.write(f"User profile exists: {hasattr(user, 'profile')}")
        
        if hasattr(user, 'profile'):
            primary_interests = list(user.profile.primary_interests.all())
            secondary_interests = list(user.profile.secondary_interests.all())
            self.stdout.write(f"Primary interests: {[i.name for i in primary_interests]}")
            self.stdout.write(f"Secondary interests: {[i.name for i in secondary_interests]}")
        
        self.stdout.write(f"\nScoring {len(posts)} posts:")
        self.stdout.write("-" * 80)
        
        scored_posts = []
        for i, post in enumerate(posts, 1):
            score = calculate_post_score(user, post, weights)
            scored_posts.append((post, score))
            
            # Get post tags
            post_tags = [tag.name for tag in post.tags.all()]
            
            self.stdout.write(
                f"{i:2d}. Post {post.id:3d} | "
                f"Score: {score:6.2f} | "
                f"Tags: {', '.join(post_tags[:3])}{'...' if len(post_tags) > 3 else ''} | "
                f"Age: {(post.created_at.strftime('%Y-%m-%d %H:%M'))}"
            )
        
        # Sort by score
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        self.stdout.write(f"\nTop 5 posts by score:")
        self.stdout.write("-" * 80)
        for i, (post, score) in enumerate(scored_posts[:5], 1):
            post_tags = [tag.name for tag in post.tags.all()]
            self.stdout.write(
                f"{i}. Post {post.id:3d} | "
                f"Score: {score:6.2f} | "
                f"Tags: {', '.join(post_tags[:3])}{'...' if len(post_tags) > 3 else ''}"
            )
        
        # Test personalized feed
        self.stdout.write(f"\nTesting personalized feed (top 5):")
        self.stdout.write("-" * 80)
        try:
            feed_posts = get_user_feed(user, limit=5, weights=weights)
            for i, post in enumerate(feed_posts, 1):
                score = calculate_post_score(user, post, weights)
                post_tags = [tag.name for tag in post.tags.all()]
                self.stdout.write(
                    f"{i}. Post {post.id:3d} | "
                    f"Score: {score:6.2f} | "
                    f"Tags: {', '.join(post_tags[:3])}{'...' if len(post_tags) > 3 else ''}"
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error getting feed: {e}"))
        
        self.stdout.write(self.style.SUCCESS("\nScoring test completed!")) 