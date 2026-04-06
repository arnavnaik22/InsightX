# InsightX: Semantic Resume Alignment with Explainable AI (XAI)

InsightX is an end-to-end AI pipeline designed to solve the "Black Box" problem in Applicant Tracking Systems (ATS). It uses **Deep Learning** to understand intent and **SHAP** to provide transparent feedback to candidates.

## 🚀 Key Innovations
- **Semantic Search:** Unlike keyword-based ATS, InsightX uses **Sentence-BERT (SBERT)** to map resumes and job descriptions into a 384-dimensional latent space.
- **Explainable AI (XAI):** Implements **Kernel SHAP** with text perturbation to visualize which specific words impacted the match score.
- **Bias Mitigation:** Built-in **spaCy NER** filters that strip out institutional names (e.g., University names) and personal names to ensure merit-based scoring.
- **Dynamic Feature Engineering:** Custom noise-filtering logic to remove linguistic filler and focus strictly on technical hard skills.

## 🛠️ Tech Stack
- **Backend:** Django, SQLite
- **ML/NLP:** Sentence-Transformers (`all-MiniLM-L6-v2`), SHAP, spaCy, Scikit-learn
- **Frontend:** Bootstrap 5, Chart.js, jQuery (AJAX)

## 📦 Local Setup
1. **Clone the repo:** `git clone <your-url>`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Download NLP Models:** `python -m spacy download en_core_web_sm`
4. **Train Local Model:** `python -m analyzer.ml.data_builder`
5. **Run Server:** `python manage.py runserver`