from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Prefetch, Count
from django.core.cache import cache
from .models import RelevanceWeight, SeenPost, Post, Interest

def calculate_post_score(user, post, weights=None):
    """
    Calculate a relevance score for a post based on user interests, freshness, and seen status.
    
    Args:
        user: Django User object
        post: Post object
        weights: RelevanceWeight object (optional, will use active weights if not provided)
    
    Returns:
        float: Score between 0 and 100
    """
    # Get weights - use provided weights or get active weights from database
    if weights is None:
        try:
            weights = RelevanceWeight.objects.filter(is_active=True).first()
        except RelevanceWeight.DoesNotExist:
            # Fallback to default weights if none configured
            weights = RelevanceWeight(
                primary_tag_weight=1.0,
                secondary_tag_weight=0.5,
                freshness_weight=0.3,
                seen_penalty=0.1
            )
    
    # Initialize base score
    base_score = 0.0
    
    # Get user profile
    try:
        user_profile = user.profile
    except:
        # If user has no profile, return 0
        return 0.0
    
    # Calculate interest matching score
    interest_score = calculate_interest_score(user_profile, post, weights)
    base_score += interest_score
    
    # Calculate freshness score
    freshness_score = calculate_freshness_score(post, weights)
    base_score += freshness_score
    
    # Apply seen penalty
    if is_post_seen_by_user(user, post):
        base_score *= weights.seen_penalty
    
    # Scale to 0-100 range
    final_score = max(0.0, min(100.0, base_score * 100))
    
    return final_score

def calculate_interest_score(user_profile, post, weights):
    """
    Calculate score based on interest matching between user and post.
    """
    score = 0.0
    
    # Get user's primary and secondary interests
    primary_interests = set(user_profile.primary_interests.all())
    secondary_interests = set(user_profile.secondary_interests.all())
    
    # Get post tags
    post_tags = set(post.tags.all())
    
    # Calculate primary interest matches
    primary_matches = len(primary_interests.intersection(post_tags))
    if primary_matches > 0:
        score += primary_matches * weights.primary_tag_weight
    
    # Calculate secondary interest matches
    secondary_matches = len(secondary_interests.intersection(post_tags))
    if secondary_matches > 0:
        score += secondary_matches * weights.secondary_tag_weight
    
    return score

def calculate_freshness_score(post, weights):
    """
    Calculate score based on post freshness (newer posts get higher scores).
    """
    now = timezone.now()
    post_age = now - post.created_at
    
    # Convert to hours for calculation
    age_hours = post_age.total_seconds() / 3600
    
    # Exponential decay: newer posts get higher scores
    # Formula: e^(-age_hours / 168) where 168 hours = 1 week
    # This gives a score that decays over time, with newer posts getting close to 1.0
    freshness_factor = max(0.0, min(1.0, 2.71828 ** (-age_hours / 168)))
    
    return freshness_factor * weights.freshness_weight

def is_post_seen_by_user(user, post):
    """
    Check if a user has already seen a post.
    """
    return SeenPost.objects.filter(user=user, post=post).exists()

def get_optimized_user_feed(user, page=1, page_size=20, weights=None, use_cache=True):
    """
    Get a personalized feed for a user with optimized database queries.
    
    Args:
        user: Django User object
        page: Page number (1-based)
        page_size: Number of posts per page
        weights: RelevanceWeight object (optional)
        use_cache: Whether to use caching (default: True)
    
    Returns:
        dict: Contains posts, pagination info, and total count
    """
    # Cache key for this user's feed
    cache_key = f"user_feed_{user.id}_page_{page}_size_{page_size}"
    
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
    
    # Get weights
    if weights is None:
        try:
            weights = RelevanceWeight.objects.filter(is_active=True).first()
        except RelevanceWeight.DoesNotExist:
            weights = RelevanceWeight(
                primary_tag_weight=1.0,
                secondary_tag_weight=0.5,
                freshness_weight=0.3,
                seen_penalty=0.1
            )
    
    # Get user profile with prefetched interests
    try:
        user_profile = user.profile
        # Prefetch interests to avoid N+1 queries
        user_profile.primary_interests.all()
        user_profile.secondary_interests.all()
    except:
        return {
            'posts': [],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_posts': 0,
                'total_pages': 0,
                'has_next': False,
                'has_previous': False
            }
        }
    
    # Get user's interest IDs for efficient filtering
    primary_interest_ids = list(user_profile.primary_interests.values_list('id', flat=True))
    secondary_interest_ids = list(user_profile.secondary_interests.values_list('id', flat=True))
    
    # Get seen post IDs
    seen_post_ids = set(SeenPost.objects.filter(user=user).values_list('post_id', flat=True))
    
    # Build optimized query
    posts_query = Post.objects.select_related().prefetch_related(
        Prefetch('tags', queryset=Interest.objects.only('id', 'name'))
    )
    
    # Exclude seen posts
    if seen_post_ids:
        posts_query = posts_query.exclude(id__in=seen_post_ids)
    
    # Get total count for pagination
    total_posts = posts_query.count()
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get posts for current page with optimized scoring
    posts = list(posts_query[offset:offset + page_size])
    
    # Batch calculate scores
    scored_posts = batch_calculate_scores(
        posts, user_profile, primary_interest_ids, 
        secondary_interest_ids, weights
    )
    
    # Sort by score (highest first)
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    
    # Prepare response
    result = {
        'posts': [post for post, score in scored_posts],
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_posts': total_posts,
            'total_pages': (total_posts + page_size - 1) // page_size,
            'has_next': offset + page_size < total_posts,
            'has_previous': page > 1
        }
    }
    
    # Cache the result for 5 minutes
    if use_cache:
        cache.set(cache_key, result, 300)
    
    return result

def batch_calculate_scores(posts, user_profile, primary_interest_ids, secondary_interest_ids, weights):
    """
    Calculate scores for multiple posts in batch to reduce database queries.
    """
    scored_posts = []
    
    for post in posts:
        score = 0.0
        
        # Calculate interest score efficiently
        post_tag_ids = set(post.tags.values_list('id', flat=True))
        
        # Primary interest matches
        primary_matches = len(set(primary_interest_ids) & post_tag_ids)
        if primary_matches > 0:
            score += primary_matches * weights.primary_tag_weight
        
        # Secondary interest matches
        secondary_matches = len(set(secondary_interest_ids) & post_tag_ids)
        if secondary_matches > 0:
            score += secondary_matches * weights.secondary_tag_weight
        
        # Calculate freshness score
        now = timezone.now()
        post_age = now - post.created_at
        age_hours = post_age.total_seconds() / 3600
        freshness_factor = max(0.0, min(1.0, 2.71828 ** (-age_hours / 168)))
        score += freshness_factor * weights.freshness_weight
        
        # Scale to 0-100 range
        final_score = max(0.0, min(100.0, score * 100))
        
        scored_posts.append((post, final_score))
    
    return scored_posts

def get_user_feed(user, limit=20, weights=None):
    """
    Legacy function for backward compatibility.
    Get a personalized feed for a user based on calculated scores.
    
    Args:
        user: Django User object
        limit: Number of posts to return
        weights: RelevanceWeight object (optional)
    
    Returns:
        list: Posts ordered by relevance score
    """
    result = get_optimized_user_feed(user, page=1, page_size=limit, weights=weights)
    return result['posts']

def mark_post_as_seen(user, post):
    """
    Mark a post as seen by a user.
    
    Args:
        user: Django User object
        post: Post object
    """
    SeenPost.objects.get_or_create(user=user, post=post)
    
    # Invalidate user's feed cache
    cache_keys = [
        f"user_feed_{user.id}_page_1_size_20",
        f"user_feed_{user.id}_page_1_size_50",
        f"user_feed_{user.id}_page_1_size_100"
    ]
    cache.delete_many(cache_keys) 