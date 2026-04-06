from rest_framework import serializers
from .models import AnalysisRecord, Skill, AnalysisSkillGap

class AnalysisSkillGapSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = AnalysisSkillGap
        fields = ['skill_name', 'severity']

class AnalysisRecordSerializer(serializers.ModelSerializer):
    skill_gaps = AnalysisSkillGapSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisRecord
        fields = ['id', 'user', 'job_description_text', 'overall_score', 'insights_json', 'created_at', 'task_id', 'status', 'skill_gaps']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']
