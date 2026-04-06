from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any extra profile fields here later if needed

    def __str__(self):
        return self.user.username

class AnalysisRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    job_description_text = models.TextField()
    resume_text = models.TextField()
    overall_score = models.FloatField(default=0.0)
    # JSON field is available in sqlite in Django 3.1+ 
    insights_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for async background processing
    task_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='COMPLETED') # e.g. PENDING, PROCESSING, COMPLETED, FAILED

    def __str__(self):
        return f"Analysis {self.id} for {self.user.username} - Score: {self.overall_score}"

class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class JobRole(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    default_jd_text = models.TextField()

    def __str__(self):
        return self.title

class AnalysisSkillGap(models.Model):
    analysis = models.ForeignKey(AnalysisRecord, on_delete=models.CASCADE, related_name='skill_gaps')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    severity = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('analysis', 'skill')

    def __str__(self):
        return f"Gap: {self.skill.name} for Analysis {self.analysis.id}"

class SavedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_resumes')
    file_upload = models.FileField(upload_to='resumes/%Y/%m/')
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume {self.id} for {self.user.username}"

class AnalysisFeedback(models.Model):
    analysis = models.ForeignKey(AnalysisRecord, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    baseline = models.ForeignKey(AnalysisRecord, on_delete=models.CASCADE, related_name='baseline_comparisons')
    target = models.ForeignKey(AnalysisRecord, on_delete=models.CASCADE, related_name='target_comparisons')
    summary_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison {self.id} for {self.user.username}"
