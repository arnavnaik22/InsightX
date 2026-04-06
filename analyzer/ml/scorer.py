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
        """Calculates the semantic match probability with conservative scaling."""
        if not self.is_trained: 
            return 0.0
        
        # Internally filters via nlp_engine.get_embeddings
        jd_vec = self.nlp_engine.get_embeddings(jd_text)
        res_vec = self.nlp_engine.get_embeddings(res_text)
        
        # Feature generation: Element-wise multiplication of vectors
        features = (jd_vec * res_vec).reshape(1, -1)
        
        # Get probability from the Logistic Regression model
        prob = self.model.predict_proba(features)[0][1]
        
        # SCALING ADJUSTMENT:
        # We lowered the multiplier from 140 to 110. 
        # This penalizes generic matches and rewards specific skill overlap.
        final_score = float(min(prob * 110, 99.0))
        
        return round(final_score, 1)

    def get_feature_vector(self, jd_text: str, res_text: str):
        """Helper for the SHAP explainer to get the raw features."""
        jd_vec = self.nlp_engine.get_embeddings(jd_text)
        res_vec = self.nlp_engine.get_embeddings(res_text)
        return (jd_vec * res_vec).reshape(1, -1)