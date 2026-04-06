# InsightX – AI‑Powered Resume–Job Fit Analyzer

InsightX is a Django‑based web application that analyzes how well a candidate’s resume matches a given job description using modern NLP and machine learning. It is designed as a **Web Programming Lab (WPL)** project and demonstrates a full‑stack pipeline:

- Django auth + models + views
- AJAX/JavaScript frontend with Chart.js
- ML scoring using Sentence Transformers + Logistic Regression
- Explainability with SHAP
- PDF parsing for resumes
- (Optional) async processing with Celery + Redis
- REST API with Django REST Framework

---

## 1. Features

### Core Features

- **User Authentication**
  - Register / Login / Logout using Django’s built‑in auth.
  - Each user has a profile and private analysis history.

- **AI Resume–Job Fit Analysis**
  - Upload a **resume PDF** and paste a **job description**.
  - Resume text is extracted with `PyPDF2`.
  - Text is cleaned and processed via a custom `NLPEngine` using:
    - `sentence-transformers` (`all-MiniLM-L6-v2`) for embeddings
    - spaCy for POS tagging and NER
  - A logistic regression model is trained on semantic features to output a **match score /100**.

- **Explainability (SHAP)**
  - SHAP values are computed for the resume text versus the job description.
  - Top **positive** and **negative** contributing keywords are shown.
  - A **horizontal bar chart** (Chart.js) visualizes contribution scores.
  - “Critical Missing Keywords” are highlighted as badges.

- **History & Persistence**
  - Each analysis is stored as an `AnalysisRecord` in the database.
  - Users can view historical scores over time.

### Extended / WPL‑Oriented Features

- **Django + AJAX Frontend**
  - Async `/analyze/` endpoint called via jQuery `$.ajax`.
  - Loading spinner and UI state (disable button, change button text).
  - Dynamic DOM updates for score, charts, and keyword badges.

- **ML & Text Processing Stack**
  - `ScorerEngine` encapsulates model loading and scoring.
  - `InsightExplainer` wraps SHAP explainability for text.
  - `NLPEngine` standardizes tech‑term extraction, NER‑based noise removal, and embedding generation.
  - `clean_text` provides additional NLTK‑based preprocessing.

- **(Optional) Celery + Redis Integration**
  - Celery workers can offload heavy model and SHAP computations to background tasks.
  - Redis serves as the message broker and result backend.
  - This demonstrates asynchronous task processing in a web application.

- **REST API (Django REST Framework)**
  - API endpoints (planned/optional) for:
    - Submitting an analysis
    - Listing user history
    - Fetching analysis details
    - Aggregating trending missing skills

---

## 2. Tech Stack

### Backend

- Python 3.11+
- Django
- Django REST Framework (DRF)
- Celery
- Redis
- SQLite (default; can be switched to PostgreSQL)

### Machine Learning / NLP

- `sentence-transformers` (SBERT)
- `scikit-learn`
- `shap`
- `spacy` (`en_core_web_sm`)
- `nltk`
- `PyPDF2`
- `joblib`
- `pandas`, `numpy`

### Frontend

- HTML5, CSS3, Bootstrap 5
- Django Templates
- jQuery
- Chart.js

---

## 3. Project Structure (simplified)

```text
insightx/
├─ manage.py
├─ insightx/                # Project settings, urls, celery app
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ celery.py
│  └─ ...
├─ analyzer/                # Main app (example name)
│  ├─ models.py             # UserProfile, AnalysisRecord, etc.
│  ├─ views.py              # home, login, register, analyze_view
│  ├─ urls.py
│  ├─ ml/
│  │  ├─ nlp_engine.py      # NLPEngine (embeddings, spaCy)
│  │  ├─ scorer.py          # ScorerEngine (LogReg model)
│  │  ├─ explainer.py       # InsightExplainer (SHAP)
│  │  └─ transformer_model.pkl / X_train_transformer.pkl (ignored or stored externally)
│  ├─ services/
│  │  ├─ pdf_extractor.py   # extract_text_from_pdf
│  │  └─ text_cleaner.py    # clean_text with NLTK
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ dashboard.html
│  │  ├─ login.html
│  │  └─ register.html
│  └─ static/
│     ├─ css/style.css
│     └─ js/main.js
└─ requirements.txt
```

---

## 4. Setup & Installation

### 4.1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 4.2. Create and Activate Virtual Environment

Using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate     # Linux / macOS
# or
.\.venv\Scripts\activate      # Windows
```

Or using Conda:

```bash
conda create -n dev python=3.11
conda activate dev
```

### 4.3. Install Dependencies

```bash
pip install -r requirements.txt
```

Additionally, download spaCy model and NLTK data (if not already automated):

```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

> Note: Large ML models or `.pkl` files may be downloaded/generated via a separate script rather than stored in Git.

### 4.4. Apply Migrations

```bash
python manage.py migrate
```

### 4.5. Create Superuser (optional)


```bash
python manage.py createsuperuser
```

---

## 5. Running the Application

### 5.1. Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

### 5.2. Starting Redis (for Celery)

On Ubuntu:

```bash
sudo systemctl start redis-server
sudo systemctl status redis-server
```

### 5.3. Starting Celery Worker (optional / async mode)

In a new terminal, with the virtualenv activated and inside project root:

```bash
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/1"

python -m celery -A insightx worker -l info
```

---

## 6. Usage Flow

1. Register a new user or log in.
2. Navigate to the dashboard / analyzer page.
3. Paste a job description (e.g., AI/ML Engineer JD).
4. Upload a resume PDF.
5. Click **“Analyze Fit”**.
6. Wait for processing; the page updates with:
   - Match score (0–100)
   - SHAP explainability bar chart
   - Critical missing keywords list
7. Previous analyses are available in the history section.

---

## 7. Testing

If you have tests configured:

```bash
pytest
# or
python manage.py test
```

---

## 8. WPL Report Pointers

For academic/portfolio documentation, highlight:

- **Web Programming Concepts**
  - Django MVC, routing, templates, static files
  - AJAX with jQuery
  - REST API (DRF)
  - Asynchronous processing (Celery + Redis)
- **ML / AI Concepts**
  - Sentence embeddings and semantic similarity
  - Logistic regression classifier
  - Explainable AI (SHAP)
- **Database & Persistence**
  - Django ORM models
  - User‑specific history and analytics

---

## 9. License

Add your preferred license here (MIT, Apache 2.0, etc.), or state that it is for academic use only.
