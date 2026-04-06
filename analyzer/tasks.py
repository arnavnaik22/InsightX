from celery import shared_task
from .models import AnalysisRecord
from .ml.scorer import ScorerEngine
from .ml.explainer import InsightExplainer
import traceback

scorer_engine = None
explainer = None

def get_engines():
    global scorer_engine, explainer
    if scorer_engine is None:
        scorer_engine = ScorerEngine()
        explainer = InsightExplainer(scorer_engine)
    return scorer_engine, explainer

@shared_task
def process_analysis(analysis_record_id):
    try:
        record = AnalysisRecord.objects.get(id=analysis_record_id)
        record.status = 'PROCESSING'
        record.save()
        
        scorer, exp = get_engines()
        
        jd_clean = scorer.nlp_engine.extract_tech_terms(record.job_description_text)
        resume_clean = scorer.nlp_engine.extract_tech_terms(record.resume_text)
        
        score = scorer.score_resume(jd_clean, resume_clean)
        explanation = exp.explain(jd_clean, resume_clean)
        
        record.overall_score = score
        record.insights_json = explanation
        record.status = 'COMPLETED'
        record.save()
        
        return {"status": "SUCCESS", "analysis_id": analysis_record_id}
    except Exception as e:
        record = AnalysisRecord.objects.get(id=analysis_record_id)
        record.status = 'FAILED'
        record.insights_json = {"error": str(e), "traceback": traceback.format_exc()}
        record.save()
        return {"status": "FAILED", "error": str(e)}
