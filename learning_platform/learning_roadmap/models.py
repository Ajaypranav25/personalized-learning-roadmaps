from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('coding', 'Coding'),
        ('language', 'Language Learning'),
        ('fitness', 'Fitness'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class LearningGoal(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    hours_per_week = models.IntegerField()
    target_duration_weeks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Roadmap(models.Model):
    goal = models.OneToOneField(LearningGoal, on_delete=models.CASCADE, related_name='roadmap')
    generated_at = models.DateTimeField(auto_now_add=True)
    ai_summary = models.TextField()
    
    def __str__(self):
        return f"Roadmap for {self.goal.title}"
    
    def get_progress_percentage(self):
        total_milestones = self.milestones.count()
        if total_milestones == 0:
            return 0
        completed = self.milestones.filter(is_completed=True).count()
        return round((completed / total_milestones) * 100, 2)


class Milestone(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    week_number = models.IntegerField()
    order = models.IntegerField()
    estimated_hours = models.FloatField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['week_number', 'order']
    
    def __str__(self):
        return f"Week {self.week_number}: {self.title}"


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('video', 'Video'),
        ('article', 'Article'),
        ('course', 'Course'),
        ('book', 'Book'),
        ('practice', 'Practice'),
        ('other', 'Other'),
    ]
    
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=300)
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    is_free = models.BooleanField(default=True)
    estimated_duration = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title


class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    hours_spent = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Progress entries"
        unique_together = ['user', 'milestone']
    
    def __str__(self):
        return f"{self.user.username} - {self.milestone.title}"
# Create your models here.
