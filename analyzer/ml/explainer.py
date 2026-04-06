import shap
import numpy as np

class InsightExplainer:
    def __init__(self, scorer_engine):
        self.scorer_engine = scorer_engine

    def _predict_pipeline(self, texts):
        scores = []
        for text in texts:
            score = self.scorer_engine.score_resume(self.current_jd, text)
            scores.append([1 - (score/100), score/100])
        return np.array(scores)

    def explain(self, jd_text_clean: str, resume_text_clean: str):
        self.current_jd = jd_text_clean 
        
        # Partition Explainer: Optimized for text perturbation
        explainer = shap.Explainer(self._predict_pipeline, masker=shap.maskers.Text(tokenizer=r"\W+"))
        shap_values = explainer([resume_text_clean])

        words = shap_values.data[0]
        values = shap_values.values[0][:, 1]

        word_contribs = {}
        for word, val in zip(words, values):
            word = word.strip().lower()
            if len(word) > 2 and val != 0:
                word_contribs[word] = word_contribs.get(word, 0) + float(val)

        sorted_items = sorted(word_contribs.items(), key=lambda x: x[1], reverse=True)
        
        missing = self.scorer_engine.nlp_engine.extract_missing_keywords(jd_text_clean, resume_text_clean)
        
        # Determine approx match buckets:
        import re
        jd_words = set([w.strip().lower() for w in re.findall(r'\b\w+\b', jd_text_clean) if len(w) > 2])
        resume_words = set([w.strip().lower() for w in re.findall(r'\b\w+\b', resume_text_clean) if len(w) > 2])
        matched_skills = list(jd_words.intersection(resume_words))
        
        score_val = self.scorer_engine.score_resume(jd_text_clean, resume_text_clean)
        
        summary = ""
        if score_val > 75:
            summary = "Great match! Your resume covers most of the core requirements."
        elif score_val > 50:
            summary = "Decent match, but missing several key technical terms."
        else:
            summary = "Low match. Consider adding the missing keywords to improve your score."
            
        actionable_next_skills = list(missing)[:3]
        if actionable_next_skills:
            summary += f" Actionable next skills to review/learn: {', '.join(actionable_next_skills)}."
        else:
            summary += " You have excellent coverage of the desired skills!"

        return {
            "top_positives": dict(sorted_items[:5]),
            "top_negatives": dict(sorted_items[-3:]),
            "missing_keywords": missing,
            "match_buckets": {
                "matched": matched_skills[:15],
                "missing": list(missing)
            },
            "summary_text": summary
        }