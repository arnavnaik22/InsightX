from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from .models import AnalysisRecord, Skill, AnalysisComparison, JobRole
from .services.pdf_extractor import extract_text_from_pdf
from .ml.scorer import ScorerEngine
from .ml.explainer import InsightExplainer
import csv
import json

# Fallback synchronous engines
scorer_engine = None
explainer = None

def get_engines():
    global scorer_engine, explainer
    if scorer_engine is None:
        scorer_engine = ScorerEngine()
        explainer = InsightExplainer(scorer_engine)
    return scorer_engine, explainer

def home(request):
    if request.user.is_authenticated:
        return redirect('analyze')
    return render(request, 'home.html', {'is_home': True})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('analyze')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('analyze')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def analyze_view(request):
    if request.method == 'POST':
        jd_text = request.POST.get('jd_text', '')
        resume_file = request.FILES.get('resume_file')
        
        if not jd_text or not resume_file:
            return JsonResponse({"status": "error", "message": "Missing JD or Resume"}, status=400)
            
        raw_resume_text = extract_text_from_pdf(resume_file)
        if not raw_resume_text:
            return JsonResponse({"status": "error", "message": "Could not read PDF"}, status=400)
            
        record = AnalysisRecord.objects.create(
            user=request.user,
            job_description_text=jd_text,
            resume_text=raw_resume_text,
            status='PENDING'
        )
        
        if getattr(settings, 'FEATURE_ASYNC_ANALYSIS', False):
            from .tasks import process_analysis
            task = process_analysis.delay(record.id)
            record.task_id = task.id
            record.save()
            return JsonResponse({
                "status": "pending", 
                "task_id": task.id,
                "analysis_id": record.id
            })
        else:
            scorer, exp = get_engines()
            jd_clean = scorer.nlp_engine.extract_tech_terms(jd_text)
            resume_clean = scorer.nlp_engine.extract_tech_terms(raw_resume_text)
            
            score = scorer.score_resume(jd_clean, resume_clean)
            explanation = exp.explain(jd_clean, resume_clean)
            
            record.overall_score = score
            record.insights_json = explanation
            record.status = 'COMPLETED'
            record.save()
            
            # For AJAX callers return JSON; for plain form POST redirect
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    "status": "success",
                    "score": score,
                    "explanation": explanation,
                    "analysis_id": record.id
                })
            return redirect('analysis_detail', pk=record.id)
    
    templates = JobRole.objects.all()
    recent = AnalysisRecord.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {'recent': recent, 'templates': templates, 'is_analyze': True})

@login_required
def analyze_status_view(request, task_id):
    try:
        record = AnalysisRecord.objects.get(task_id=task_id, user=request.user)
    except AnalysisRecord.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Not found"}, status=404)
        
    return JsonResponse({
        "status": record.status, 
        "score": record.overall_score, 
        "explanation": record.insights_json,
        "analysis_id": record.id
    })

@login_required
def history_view(request):
    query = AnalysisRecord.objects.filter(user=request.user).order_by('-created_at')
    
    search = request.GET.get('q', '')
    if search:
        query = query.filter(job_description_text__icontains=search)
        
    paginator = Paginator(query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'history.html', {'page_obj': page_obj, 'is_history': True, 'query': search})

@login_required
def analysis_detail_view(request, pk):
    record = get_object_or_404(AnalysisRecord, pk=pk, user=request.user)
    return render(request, 'analysis_detail.html', {'analysis': record})

@login_required
def compare_view(request):
    if request.method == 'POST':
        base_id = request.POST.get('base_id')
        target_id = request.POST.get('target_id')
        base = get_object_or_404(AnalysisRecord, pk=base_id, user=request.user)
        target = get_object_or_404(AnalysisRecord, pk=target_id, user=request.user)
        
        return render(request, 'compare.html', {
            'base': base,
            'target': target,
            'score_delta': target.overall_score - base.overall_score
        })
        
    records = AnalysisRecord.objects.filter(user=request.user, status='COMPLETED').order_by('-created_at')
    return render(request, 'compare_select.html', {'records': records, 'is_compare': True})

@login_required
def profile_view(request):
    total = AnalysisRecord.objects.filter(user=request.user).count()
    return render(request, 'profile.html', {'total_analyses': total, 'user': request.user})

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_analytics_view(request):
    import django.contrib.auth.models
    total_users = django.contrib.auth.models.User.objects.count()
    total_analyses = AnalysisRecord.objects.count()
    from django.db.models import Avg
    avg_score = AnalysisRecord.objects.filter(status='COMPLETED').aggregate(Avg('overall_score'))['overall_score__avg']
    return render(request, 'admin_analytics.html', {
        'total_analyses': total_analyses,
        'avg_score': avg_score,
        'total_users': total_users,
        'is_admin': True
    })

@login_required
def export_history_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="history_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Score', 'Status'])

    for obj in AnalysisRecord.objects.filter(user=request.user).order_by('-created_at'):
        writer.writerow([obj.id, obj.created_at, obj.overall_score, obj.status])

    return response

@login_required
def export_pdf_view(request, pk):
    record = get_object_or_404(AnalysisRecord, pk=pk, user=request.user)
    from reportlab.pdfgen import canvas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{record.id}.pdf"'
    
    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Analysis Report for {request.user.username}")
    p.drawString(100, 780, f"Score: {record.overall_score:.2f}%")
    p.drawString(100, 760, f"Date: {record.created_at.strftime('%Y-%m-%d %H:%M')}")
    # Needs more robust generation
    p.drawString(100, 740, "Strengths & Weaknesses Detailed View Available on App")
    p.showPage()
    p.save()
    return response