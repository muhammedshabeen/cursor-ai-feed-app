import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from feed_app.utils import get_optimized_user_feed, get_user_feed
from feed_app.models import RelevanceWeight

class Command(BaseCommand):
    help = 'Test the performance of optimized feed generation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Test performance for specific user ID'
        )
        parser.add_argument(
            '--page-size',
            type=int,
            default=20,
            help='Page size for testing (default: 20)'
        )
        parser.add_argument(
            '--iterations',
            type=int,
            default=3,
            help='Number of iterations to test (default: 3)'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        page_size = options['page_size']
        iterations = options['iterations']
        
        # Get or create a test user
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} does not exist"))
                return
        else:
            # Use the first user with a profile
            user = User.objects.filter(profile__isnull=False).first()
            if not user:
                self.stdout.write(self.style.ERROR("No users with profiles found"))
                return
        
        self.stdout.write(f"Testing feed performance for user: {user.username}")
        self.stdout.write(f"Page size: {page_size}, Iterations: {iterations}")
        self.stdout.write("-" * 60)
        
        # Test optimized feed
        self.stdout.write("Testing OPTIMIZED feed generation:")
        optimized_times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = get_optimized_user_feed(
                user=user,
                page=1,
                page_size=page_size,
                use_cache=True
            )
            end_time = time.time()
            duration = end_time - start_time
            optimized_times.append(duration)
            
            self.stdout.write(f"  Iteration {i+1}: {duration:.4f}s - {len(result['posts'])} posts")
            self.stdout.write(f"    Total posts: {result['pagination']['total_posts']}")
            self.stdout.write(f"    Cache hit: {'Yes' if i > 0 else 'No'}")
        
        avg_optimized = sum(optimized_times) / len(optimized_times)
        self.stdout.write(f"  Average optimized time: {avg_optimized:.4f}s")
        
        # Test legacy feed (without cache)
        self.stdout.write("\nTesting LEGACY feed generation (no cache):")
        legacy_times = []
        
        for i in range(iterations):
            start_time = time.time()
            posts = get_user_feed(user=user, limit=page_size)
            end_time = time.time()
            duration = end_time - start_time
            legacy_times.append(duration)
            
            self.stdout.write(f"  Iteration {i+1}: {duration:.4f}s - {len(posts)} posts")
        
        avg_legacy = sum(legacy_times) / len(legacy_times)
        self.stdout.write(f"  Average legacy time: {avg_legacy:.4f}s")
        
        # Performance comparison
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("PERFORMANCE COMPARISON:")
        self.stdout.write(f"  Optimized (with cache): {avg_optimized:.4f}s")
        self.stdout.write(f"  Legacy (no cache):      {avg_legacy:.4f}s")
        
        if avg_legacy > 0:
            improvement = ((avg_legacy - avg_optimized) / avg_legacy) * 100
            self.stdout.write(f"  Performance improvement: {improvement:.1f}%")
        
        # Cache effectiveness
        if len(optimized_times) > 1:
            first_call = optimized_times[0]
            cached_calls = optimized_times[1:]
            avg_cached = sum(cached_calls) / len(cached_calls)
            cache_improvement = ((first_call - avg_cached) / first_call) * 100
            self.stdout.write(f"  Cache effectiveness: {cache_improvement:.1f}% improvement")
        
        self.stdout.write(self.style.SUCCESS("\nPerformance test completed!")) 