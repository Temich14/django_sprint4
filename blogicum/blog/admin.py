from django.contrib import admin
from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'location', 'is_published',
        'pub_date', 'created_at'
    )
    list_editable = ('is_published', 'category', 'location')
    list_filter = (
        'is_published', 'category', 'location', 'author', 'pub_date',
        'created_at'
    )
    search_fields = ('title', 'text')
    list_per_page = 20
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'text')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'post__title')
    date_hierarchy = 'created_at'
