from django.contrib import admin
from .models import Post, Hero, Listing, UserProfile


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created']
    search_fields = ['title', 'body']


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'phone', 'email', 'is_active', 'order']
    list_filter   = ['category', 'is_active']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'tagline', 'description_en', 'description_ro', 'description_ru']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'photo', 'tagline', 'is_active', 'order'),
        }),
        ('Descriptions', {
            'fields': ('description_en', 'description_ro', 'description_ru', 'services'),
            'classes': ('wide',),
        }),
        ('Contact', {
            'fields': ('phone', 'email'),
        }),
    )


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display  = ['title', 'owner', 'price', 'is_active', 'created']
    list_filter   = ['is_active']
    search_fields = ['title', 'description', 'owner__username']
    readonly_fields = ['created', 'updated']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'email_confirmed']
    list_filter   = ['email_confirmed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user']
