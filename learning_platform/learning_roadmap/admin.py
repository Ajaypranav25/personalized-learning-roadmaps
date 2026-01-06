from django.contrib import admin

from .models import Category, LearningGoal, Roadmap, Milestone, Resource, Progress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'difficulty_level', 'created_at']
    list_filter = ['category', 'difficulty_level', 'is_active']
    search_fields = ['title', 'user__username']

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['goal', 'generated_at']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'week_number', 'is_completed']
    list_filter = ['is_completed', 'week_number']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'is_free', 'is_completed']
    list_filter = ['resource_type', 'is_free', 'is_completed']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'milestone', 'hours_spent', 'updated_at']
# Register your models here.
