from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Web Routes
    path('', views.home, name='home'),
    path('analyze/', views.analyze_view, name='analyze'),
    path('history/', views.history_view, name='history'),
    path('analysis/<int:pk>/', views.analysis_detail_view, name='analysis_detail'),
    path('compare/', views.compare_view, name='compare'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-analytics/', views.admin_analytics_view, name='admin_analytics'),
    
    # Export Routes
    path('export/pdf/<int:pk>/', views.export_pdf_view, name='export_pdf'),
    path('export/csv/', views.export_history_csv_view, name='export_csv'),
    
    # Async Status Polling
    path('analyze/status/<str:task_id>/', views.analyze_status_view, name='analyze_status'),

    # REST APIs
    path('api/analyze/', api.AnalyzeAPIView.as_view(), name='api_analyze'),
    path('api/history/', api.HistoryAPIView.as_view(), name='api_history'),
    path('api/analysis/<int:pk>/', api.AnalysisDetailAPIView.as_view(), name='api_analysis_detail'),
]
