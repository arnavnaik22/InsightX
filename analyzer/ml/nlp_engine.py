import spacy
import re
import numpy as np
from sentence_transformers import SentenceTransformer

class NLPEngine:
    def __init__(self):
        # 1. Load the SBERT Transformer (Semantic Brain)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Load spaCy for POS tagging and NER (Logic Brain)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def extract_tech_terms(self, text: str) -> str:
        """
        Cleans text of special characters and filters for hard skills.
        Removes institutional names, people, and geopolitical noise.
        """
        # A. Strip all special characters/punctuation (kills bullets like • or |)
        clean_raw = re.sub(r'[^\w\s]', ' ', str(text))
        
        # B. Process with spaCy
        doc = self.nlp(clean_raw)
        
        # C. Aggressive Noise List (Broad terms that don't help differentiate)
        noise_words = {
            'using', 'point', 'work', 'team', 'department', 'capability', 
            'manipal', 'technology', 'system', 'process', 'result', 
            'standard', 'environment', 'accuracyon', 'clinical', 'text',
            'ability', 'analysis', 'application', 'architecture', 'build', 
            'builder', 'building', 'code', 'collaboration', 'designing',
            'intersection', 'foundation', 'deployment', 'hand', 'university',
            'institute', 'student', 'semester', 'synopsis', 'india', 
            'engineering', 'engineer', 'development', 'developer', 'project'
        } 
        
        # D. Use NER to ignore People (PERSON) and Countries/Cities (GPE)
        entities_to_ignore = {ent.text.lower() for ent in doc.ents if ent.label_ in ["PERSON", "GPE"]}
        
        terms = []
        for token in doc:
            term = token.lemma_.lower().strip()
            
            # Filter Logic:
            # - Nouns/Proper Nouns only
            # - Not a stop word
            # - Not in noise list
            # - Not an entity name
            # - Length > 2
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                term not in noise_words and 
                term not in entities_to_ignore and
                len(term) > 2):
                
                # Standardize artifacts
                if term == "datum":
                    term = "data"
                
                terms.append(term)
                
        return " ".join(terms)

    def get_embeddings(self, text: str) -> np.ndarray:
        """Converts tech-filtered text into a 384-dimensional semantic vector."""
        filtered_text = self.extract_tech_terms(text)
        if not filtered_text.strip():
            return np.zeros(384)
        return self.model.encode([filtered_text])[0]

    def extract_missing_keywords(self, jd_text: str, resume_text: str, top_n: int = 12) -> list[str]:
        """Identifies missing technical gaps by comparing filtered nouns."""
        jd_terms = set(self.extract_tech_terms(jd_text).split())
        res_terms = set(self.extract_tech_terms(resume_text).split())
        
        missing = list(jd_terms - res_terms)
        return sorted(missing)[:top_n]