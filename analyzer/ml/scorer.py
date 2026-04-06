import os
import joblib
import numpy as np
from analyzer.ml.nlp_engine import NLPEngine

class ScorerEngine:
    def __init__(self):
        self.nlp_engine = NLPEngine()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            self.model = joblib.load(os.path.join(current_dir, 'transformer_model.pkl'))
            self.X_train = joblib.load(os.path.join(current_dir, 'X_train_transformer.pkl'))
            self.is_trained = True
        except:
            self.is_trained = False

    def score_resume(self, jd_text: str, res_text: str) -> float:
        """Calculates a robust score using Semantic Cosine Similarity and Exact Keyword Matching."""
        
        # 1. Semantic Match via SBERT embeddings
        jd_vec = self.nlp_engine.get_embeddings(jd_text)
        res_vec = self.nlp_engine.get_embeddings(res_text)
        
        # Calculate Cosine Similarity
        norm_jd = np.linalg.norm(jd_vec)
        norm_res = np.linalg.norm(res_vec)
        
        if norm_jd == 0 or norm_res == 0:
            cosine_sim = 0.0
        else:
            cosine_sim = np.dot(jd_vec, res_vec) / (norm_jd * norm_res)
            
        # Map SBERT score (typically 0.1 - 0.7 for resumes) to a 0-100 scale
        semantic_score = max(0, min((cosine_sim * 100) * 1.3, 100))
        
        # 2. Hard Keyword Match
        jd_terms = set(self.nlp_engine.extract_tech_terms(jd_text).split())
        res_terms = set(self.nlp_engine.extract_tech_terms(res_text).split())
        
        if len(jd_terms) == 0:
            keyword_score = semantic_score # Fallback if JD has no extractable keywords
        else:
            overlap = len(jd_terms.intersection(res_terms))
            keyword_score = (overlap / len(jd_terms)) * 100
            
        # 3. Final Blended Score (60% Semantic understanding, 40% exact keyword match)
        final_score = (semantic_score * 0.6) + (keyword_score * 0.4)
        
        return round(float(final_score), 1)

    def get_feature_vector(self, jd_text: str, res_text: str):
        """Helper for the SHAP explainer to get the raw features."""
        jd_vec = self.nlp_engine.get_embeddings(jd_text)
        res_vec = self.nlp_engine.get_embeddings(res_text)
        return (jd_vec * res_vec).reshape(1, -1)