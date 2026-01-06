# learning_roadmap/forms.py

from django import forms
from .models import LearningGoal, Category

class LearningGoalForm(forms.ModelForm):
    class Meta:
        model = LearningGoal
        fields = ['category', 'title', 'description', 'difficulty_level', 
                  'hours_per_week', 'target_duration_weeks']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Learn Python for Data Science'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what you want to achieve and any specific areas of focus...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'hours_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 168,
                'placeholder': 'Hours per week'
            }),
            'target_duration_weeks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 52,
                'placeholder': 'Number of weeks'
            })
        }
        
        labels = {
            'title': 'Goal Title',
            'description': 'Description',
            'category': 'Category',
            'difficulty_level': 'Current Level',
            'hours_per_week': 'Hours Available Per Week',
            'target_duration_weeks': 'Target Duration (weeks)'
        }