
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import LearningGoal, Roadmap, Milestone, Resource, Progress, Category
from .forms import LearningGoalForm
from .services.gemini_service import GeminiRoadmapGenerator

@login_required
def dashboard(request):
    """User dashboard showing all goals and progress"""
    goals = LearningGoal.objects.filter(user=request.user, is_active=True)
    
    goals_with_progress = []
    for goal in goals:
        if hasattr(goal, 'roadmap'):
            progress = goal.roadmap.get_progress_percentage()
        else:
            progress = 0
        goals_with_progress.append({
            'goal': goal,
            'progress': progress
        })
    
    context = {
        'goals_with_progress': goals_with_progress
    }
    return render(request, 'learning_roadmap/dashboard.html', context)


@login_required
def create_goal(request):
    """Create a new learning goal"""
    if request.method == 'POST':
        form = LearningGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            
            # Generate roadmap using Gemini
            try:
                generator = GeminiRoadmapGenerator()
                goal_data = {
                    'title': goal.title,
                    'description': goal.description,
                    'category': goal.category.name,
                    'difficulty_level': goal.difficulty_level,
                    'hours_per_week': goal.hours_per_week,
                    'target_duration_weeks': goal.target_duration_weeks
                }
                
                roadmap_data = generator.generate_roadmap(goal_data)
                
                # Create roadmap
                roadmap = Roadmap.objects.create(
                    goal=goal,
                    ai_summary=roadmap_data['summary']
                )
                
                # Create milestones and resources
                for idx, milestone_data in enumerate(roadmap_data['milestones'], 1):
                    milestone = Milestone.objects.create(
                        roadmap=roadmap,
                        title=milestone_data['title'],
                        description=milestone_data['description'],
                        week_number=milestone_data['week_number'],
                        order=idx,
                        estimated_hours=milestone_data['estimated_hours']
                    )
                    
                    # Create resources for this milestone
                    for resource_data in milestone_data.get('resources', []):
                        Resource.objects.create(
                            milestone=milestone,
                            title=resource_data['title'],
                            url=resource_data['url'],
                            resource_type=resource_data['resource_type'],
                            is_free=resource_data['is_free'],
                            estimated_duration=resource_data.get('estimated_duration', ''),
                            description=resource_data.get('description', '')
                        )
                
                messages.success(request, 'Goal created and roadmap generated successfully!')
                return redirect('roadmap_detail', goal_id=goal.id)
            
            except Exception as e:
                messages.error(request, f'Error generating roadmap: {str(e)}')
                goal.delete()
                return redirect('create_goal')
    else:
        form = LearningGoalForm()
    
    return render(request, 'learning_roadmap/create_goal.html', {'form': form})


@login_required
def roadmap_detail(request, goal_id):
    """View detailed roadmap for a goal"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    if not hasattr(goal, 'roadmap'):
        messages.error(request, 'No roadmap found for this goal.')
        return redirect('dashboard')
    
    roadmap = goal.roadmap
    milestones = roadmap.milestones.prefetch_related('resources').all()
    
    # Group milestones by week
    weeks = {}
    for milestone in milestones:
        week = milestone.week_number
        if week not in weeks:
            weeks[week] = []
        weeks[week].append(milestone)
    
    context = {
        'goal': goal,
        'roadmap': roadmap,
        'weeks': dict(sorted(weeks.items())),
        'progress_percentage': roadmap.get_progress_percentage()
    }
    
    return render(request, 'learning_roadmap/roadmap_detail.html', context)


@login_required
def complete_milestone(request, milestone_id):
    """Mark a milestone as completed"""
    if request.method == 'POST':
        milestone = get_object_or_404(Milestone, id=milestone_id)
        
        # Check if user owns this goal
        if milestone.roadmap.goal.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        milestone.is_completed = not milestone.is_completed
        if milestone.is_completed:
            milestone.completed_at = timezone.now()
        else:
            milestone.completed_at = None
        milestone.save()
        
        # Update or create progress entry
        hours_spent = float(request.POST.get('hours_spent', 0))
        notes = request.POST.get('notes', '')
        
        progress, created = Progress.objects.get_or_create(
            user=request.user,
            milestone=milestone,
            defaults={'hours_spent': hours_spent, 'notes': notes}
        )
        
        if not created:
            progress.hours_spent = hours_spent
            progress.notes = notes
            progress.save()
        
        return JsonResponse({
            'success': True,
            'is_completed': milestone.is_completed,
            'progress_percentage': milestone.roadmap.get_progress_percentage()
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def complete_resource(request, resource_id):
    """Mark a resource as completed"""
    if request.method == 'POST':
        resource = get_object_or_404(Resource, id=resource_id)
        
        # Check if user owns this goal
        if resource.milestone.roadmap.goal.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        resource.is_completed = not resource.is_completed
        if resource.is_completed:
            resource.completed_at = timezone.now()
        else:
            resource.completed_at = None
        resource.save()
        
        return JsonResponse({
            'success': True,
            'is_completed': resource.is_completed
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_goal(request, goal_id):
    """Delete a learning goal"""
    if request.method == 'POST':
        goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
        goal.delete()
        messages.success(request, 'Goal deleted successfully.')
    
    return redirect('dashboard')