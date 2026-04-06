from django.contrib import admin
from .models import (
    UserProfile, AnalysisRecord, Skill, JobRole,
    AnalysisSkillGap, SavedResume, AnalysisFeedback, AnalysisComparison
)

admin.site.register(UserProfile)

@admin.register(AnalysisRecord)
class AnalysisRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'overall_score', 'task_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'task_id')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(AnalysisSkillGap)
class AnalysisSkillGapAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'skill', 'severity')
    list_filter = ('severity',)
    search_fields = ('skill__name', 'analysis__user__username')

@admin.register(SavedResume)
class SavedResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_upload', 'uploaded_at')
    search_fields = ('user__username',)

@admin.register(AnalysisFeedback)
class AnalysisFeedbackAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(AnalysisComparison)
class AnalysisComparisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'baseline', 'target', 'created_at')
