import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from url_features import build_feature_matrix


# -------------------------
# Load dataset
# -------------------------
_here = os.path.dirname(os.path.abspath(__file__))
_data_path = os.path.join(_here, "data", "phiusiil_url.csv")
df = pd.read_csv(_data_path)
df = df[["URL", "label"]].dropna()

# Label fix: 1=legit -> 0, 0=phishing -> 1
df["label"] = df["label"].map({1: 0, 0: 1})

X = df["URL"].astype(str)
y = df["label"].astype(int)

# -------------------------
# Train-test split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# -------------------------
# Vectorizer (character n-grams)
# -------------------------
vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 6),
    min_df=3,
    max_df=0.9,
    sublinear_tf=True
)
vectorizer.fit(X_train)

# -------------------------
# Feature matrices
# -------------------------
X_train_vec = build_feature_matrix(X_train, vectorizer)
X_test_vec = build_feature_matrix(X_test, vectorizer)

# -------------------------
# Model
# -------------------------
model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced"
)
model.fit(X_train_vec, y_train)

# -------------------------
# Evaluation
# -------------------------
y_pred = model.predict(X_test_vec)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------
# Save
# -------------------------
_model_dir = os.path.join(_here, "model")
os.makedirs(_model_dir, exist_ok=True)
joblib.dump(model, os.path.join(_model_dir, "url_model.pkl"))
joblib.dump(vectorizer, os.path.join(_model_dir, "url_vectorizer.pkl"))

print("\nURL phishing model trained with structural + lexical features")
