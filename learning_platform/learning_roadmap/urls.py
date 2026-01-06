from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('goal/create/', views.create_goal, name='create_goal'),
    path('goal/<int:goal_id>/', views.roadmap_detail, name='roadmap_detail'),
    path('goal/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('milestone/<int:milestone_id>/complete/', views.complete_milestone, name='complete_milestone'),
    path('resource/<int:resource_id>/complete/', views.complete_resource, name='complete_resource'),
]