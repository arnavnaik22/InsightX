from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AnalysisRecord, Skill
from .serializers import AnalysisRecordSerializer
from .tasks import process_analysis
from django.conf import settings

class AnalyzeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        jd_text = request.data.get('jd_text', '')
        resume_file = request.FILES.get('resume_file')
        
        if not jd_text or not resume_file:
            return Response({"error": "Missing jd_text or resume_file"}, status=400)
            
        # extract text here
        from .services.pdf_extractor import extract_text_from_pdf
        raw_resume_text = extract_text_from_pdf(resume_file)
        
        if not raw_resume_text:
            return Response({"error": "Could not extract text from PDF"}, status=400)
            
        record = AnalysisRecord.objects.create(
            user=request.user,
            job_description_text=jd_text,
            resume_text=raw_resume_text,
            status='PENDING'
        )
        
        if getattr(settings, 'FEATURE_ASYNC_ANALYSIS', False):
            task = process_analysis.delay(record.id)
            record.task_id = task.id
            record.save()
            return Response({
                "message": "Analysis started asynchronously",
                "task_id": task.id,
                "analysis_id": record.id
            })
        else:
            # Synchronous processing
            process_analysis(record.id)
            record.refresh_from_db()
            serializer = AnalysisRecordSerializer(record)
            return Response(serializer.data)

class HistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = AnalysisRecord.objects.filter(user=request.user).order_by('-created_at')
        serializer = AnalysisRecordSerializer(records, many=True)
        return Response(serializer.data)

class AnalysisDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            record = AnalysisRecord.objects.get(pk=pk, user=request.user)
            serializer = AnalysisRecordSerializer(record)
            return Response(serializer.data)
        except AnalysisRecord.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
