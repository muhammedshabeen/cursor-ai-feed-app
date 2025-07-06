from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Interest(models.Model):
    """Model for user interests/tags like 'music', 'sports', etc."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Extended user profile with interests"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    primary_interests = models.ManyToManyField(Interest, related_name='primary_users', blank=True)
    secondary_interests = models.ManyToManyField(Interest, related_name='secondary_users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Post(models.Model):
    """Model for posts with images, text, and tags"""
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    text = models.TextField()
    tags = models.ManyToManyField(Interest, related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class SeenPost(models.Model):
    """Model to track which users have seen which posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='seen_by')
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-seen_at']

    def __str__(self):
        return f"{self.user.username} saw post {self.post.id} at {self.seen_at}"

class RelevanceWeight(models.Model):
    """Model to hold tunable weights for post scoring algorithm"""
    name = models.CharField(max_length=100, unique=True, help_text="Name for this weight configuration")
    primary_tag_weight = models.FloatField(default=1.0, help_text="Weight for posts matching primary interests")
    secondary_tag_weight = models.FloatField(default=0.5, help_text="Weight for posts matching secondary interests")
    freshness_weight = models.FloatField(default=0.3, help_text="Weight for post freshness (newer posts get higher scores)")
    seen_penalty = models.FloatField(default=0.1, help_text="Penalty multiplier for posts already seen by user")
    is_active = models.BooleanField(default=True, help_text="Whether this configuration is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.name} (Active: {self.is_active})"

    def save(self, *args, **kwargs):
        # Ensure only one configuration is active at a time
        if self.is_active:
            RelevanceWeight.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

# Signal to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    instance.profile.save()
