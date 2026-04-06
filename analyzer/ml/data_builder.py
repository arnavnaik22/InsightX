import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.linear_model import LogisticRegression
from analyzer.ml.nlp_engine import NLPEngine

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from analyzer.services.text_cleaner import clean_text

def build_transformer_model():
    print("Loading datasets...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resumes_df = pd.read_csv(os.path.join(current_dir, 'raw_data', 'UpdatedResumeDataSet.csv')).dropna()
    jobs_df = pd.read_csv(os.path.join(current_dir, 'raw_data', 'postings.csv')).dropna(subset=['title', 'description'])

    nlp = NLPEngine()
    X = []
    y = []

    print("Generating Semantic Embeddings (This uses the Transformer)...")
    for category in resumes_df['Category'].unique():
        cat_res = resumes_df[resumes_df['Category'] == category]['Resume'].tolist()[:30]
        search_term = category.split()[0].lower()
        matching_jobs = jobs_df[jobs_df['title'].str.lower().str.contains(search_term)]['description'].tolist()[:30]
        
        for i in range(min(len(cat_res), len(matching_jobs))):
            res_vec = nlp.get_embeddings(clean_text(cat_res[i]))
            jd_vec = nlp.get_embeddings(clean_text(matching_jobs[i]))
            
            # Feature engineering: Element-wise product of embeddings
            X.append(res_vec * jd_vec)
            y.append(1)
            
            # Create a mismatch (Negative sample)
            random_jd = nlp.get_embeddings(clean_text(jobs_df.sample(1)['description'].values[0]))
            X.append(res_vec * random_jd)
            y.append(0)

    X = np.array(X)
    y = np.array(y)

    print("Training Logistic Regression on Embeddings...")
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)

    joblib.dump(clf, os.path.join(current_dir, 'transformer_model.pkl'))
    joblib.dump(X, os.path.join(current_dir, 'X_train_transformer.pkl'))
    print("Transformer Pipeline Ready!")

if __name__ == "__main__":
    build_transformer_model()