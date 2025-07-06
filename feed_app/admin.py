from django.contrib import admin
from .models import Interest, UserProfile, Post, SeenPost, RelevanceWeight

# Register your models here.

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['primary_interests', 'secondary_interests']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_preview', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['text']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'

@admin.register(SeenPost)
class SeenPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'seen_at']
    list_filter = ['seen_at']
    search_fields = ['user__username', 'post__text']
    readonly_fields = ['seen_at']

@admin.register(RelevanceWeight)
class RelevanceWeightAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_tag_weight', 'secondary_tag_weight', 'freshness_weight', 'seen_penalty', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Scoring Weights', {
            'fields': ('primary_tag_weight', 'secondary_tag_weight', 'freshness_weight', 'seen_penalty'),
            'description': 'Configure the weights used in the post scoring algorithm'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        # Ensure only one configuration is active at a time
        if obj.is_active:
            RelevanceWeight.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
