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
        matched_count = len(matched_skills)
        missing_count = len(missing)

        # Tier-based headline
        if score_val >= 80:
            tier = "Excellent Match"
            opener = (
                f"Your resume is a strong fit for this role, scoring {score_val:.0f}/100. "
                f"You demonstrate solid alignment with {matched_count} key requirement{'s' if matched_count != 1 else ''} "
                f"from the job description."
            )
        elif score_val >= 60:
            tier = "Good Match"
            opener = (
                f"Your resume is a competitive candidate for this position with a score of {score_val:.0f}/100. "
                f"You match {matched_count} skill{'s' if matched_count != 1 else ''} from the JD, "
                f"though there is room to strengthen your profile."
            )
        elif score_val >= 40:
            tier = "Partial Match"
            opener = (
                f"Your resume shows a moderate alignment with this role ({score_val:.0f}/100). "
                f"While {matched_count} keyword{'s' if matched_count != 1 else ''} overlap, "
                f"there are {missing_count} notable gap{'s' if missing_count != 1 else ''} that may reduce your chances."
            )
        else:
            tier = "Low Match"
            opener = (
                f"Your resume has limited alignment with this job description (score: {score_val:.0f}/100). "
                f"Only {matched_count} keyword{'s' if matched_count != 1 else ''} overlap with the role's requirements. "
                f"Significant upskilling or resume tailoring is recommended."
            )

        # Skill gap advice
        top_missing = list(missing)[:4]
        if top_missing:
            gap_advice = (
                f" The most impactful missing skills to add or highlight are: "
                f"{', '.join(t.title() for t in top_missing)}."
            )
        else:
            gap_advice = (
                f" Impressively, you appear to cover all extracted keywords from the job description. "
                f"Focus on tailoring the phrasing and context of your experience to further stand out."
            )

        # Matched skills highlight
        if matched_count > 0:
            sample_matched = ', '.join(s.title() for s in matched_skills[:5])
            strength_note = f" Your strongest overlapping skills include: {sample_matched}."
        else:
            strength_note = ""

        summary = opener + gap_advice + strength_note

        # Convert raw SHAP scores to % contribution labels for display (user-friendly)
        total_pos = sum(v for v in word_contribs.values() if v > 0) or 1
        top_positives_display = {
            word: round((val / total_pos) * 100, 1)
            for word, val in sorted_items[:6] if val > 0
        }

        return {
            "tier": tier,
            "top_positives": top_positives_display,
            "top_negatives": dict(sorted_items[-3:]),
            "missing_keywords": missing,
            "match_buckets": {
                "matched": matched_skills[:15],
                "missing": list(missing)
            },
            "summary_text": summary
        }