# learning_roadmap/services/gemini_service.py

import os
import json
from decouple import config
import google.generativeai as genai
from typing import Dict, List

class GeminiRoadmapGenerator:
    def __init__(self):
        # Configure Gemini API using python-decouple
        api_key = config('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_roadmap(self, goal_data: Dict) -> Dict:
        """
        Generate a learning roadmap based on user goals
        
        Args:
            goal_data: Dictionary containing:
                - title: Goal title
                - description: Goal description
                - category: Learning category
                - difficulty_level: beginner/intermediate/advanced
                - hours_per_week: Available hours per week
                - target_duration_weeks: Target completion time
        
        Returns:
            Dictionary with roadmap structure
        """
        prompt = self._create_roadmap_prompt(goal_data)
        
        try:
            response = self.model.generate_content(prompt)
            roadmap_data = self._parse_response(response.text)
            return roadmap_data
        except Exception as e:
            raise Exception(f"Error generating roadmap: {str(e)}")
    
    def _create_roadmap_prompt(self, goal_data: Dict) -> str:
        """Create a structured prompt for Gemini"""
        return f"""
You are an expert learning advisor. Create a detailed, week-by-week learning roadmap for the following goal:

**Goal Title:** {goal_data['title']}
**Description:** {goal_data['description']}
**Category:** {goal_data['category']}
**Difficulty Level:** {goal_data['difficulty_level']}
**Available Time:** {goal_data['hours_per_week']} hours per week
**Target Duration:** {goal_data['target_duration_weeks']} weeks

Please create a structured learning roadmap with the following:

1. A brief summary (2-3 sentences) explaining the learning path
2. Weekly milestones broken down by week number
3. For each milestone, include:
   - A clear title
   - Description of what will be learned
   - Estimated hours needed
   - 3-5 specific learning resources (mix of free and paid)

For each resource, provide:
- Title
- URL (use real, accessible resources like YouTube, Coursera, Udemy, freeCodeCamp, MDN, Khan Academy, etc.)
- Type (video/article/course/book/practice)
- Whether it's free or paid
- Estimated duration

Return your response in the following JSON format:
{{
  "summary": "Brief overview of the learning path",
  "milestones": [
    {{
      "week_number": 1,
      "title": "Milestone title",
      "description": "What the learner will achieve",
      "estimated_hours": 5,
      "resources": [
        {{
          "title": "Resource title",
          "url": "https://example.com",
          "resource_type": "video",
          "is_free": true,
          "estimated_duration": "2 hours",
          "description": "Brief description"
        }}
      ]
    }}
  ]
}}

Make sure the roadmap is realistic, progressive, and tailored to the {goal_data['difficulty_level']} level.
"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini's response into structured data"""
        try:
            # Remove markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            clean_text = clean_text.strip()
            roadmap_data = json.loads(clean_text)
            
            # Validate structure
            if 'summary' not in roadmap_data or 'milestones' not in roadmap_data:
                raise ValueError("Invalid roadmap structure")
            
            return roadmap_data
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
    
    def suggest_resources(self, topic: str, difficulty: str, count: int = 5) -> List[Dict]:
        """
        Suggest additional resources for a specific topic
        """
        prompt = f"""
Suggest {count} high-quality learning resources for the following topic:

**Topic:** {topic}
**Difficulty Level:** {difficulty}

Provide a mix of free and paid resources including videos, articles, and courses.
Return as a JSON array with this structure:
[
  {{
    "title": "Resource title",
    "url": "https://example.com",
    "resource_type": "video",
    "is_free": true,
    "estimated_duration": "1 hour",
    "description": "Brief description"
  }}
]
"""
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            resources = json.loads(clean_text.strip())
            return resources
        except Exception as e:
            raise Exception(f"Error suggesting resources: {str(e)}")