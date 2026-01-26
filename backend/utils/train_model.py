import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# -------- Load SMS spam dataset --------
sms = pd.read_csv("data/sms_spam.csv", encoding="latin-1")
sms = sms.iloc[:, :2]
sms.columns = ["label", "text"]
sms["label"] = sms["label"].map({"ham": 0, "spam": 1})

# -------- Load phishing email dataset --------
email = pd.read_csv("data/phishing_email.csv")
email = email[["body", "label"]]
email.columns = ["text", "label"]
email["label"] = email["label"].astype(int)

# -------- Combine both datasets --------
data = pd.concat([sms, email], ignore_index=True)
data.dropna(inplace=True)

X = data["text"]
y = data["label"]

# -------- Train-Test Split (IMPORTANT) --------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -------- Vectorization --------
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1, 2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# -------- Model --------
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# -------- Evaluation --------
y_pred = model.predict(X_test_vec)

print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# -------- Save Model & Vectorizer --------
joblib.dump(model, "model/phishing_model.pkl")
joblib.dump(vectorizer, "model/vectorizer.pkl")

print("\n✅ Model & Vectorizer saved successfully")
