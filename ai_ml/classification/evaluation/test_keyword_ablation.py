import csv
import re

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


DATASET = "ai_ml/data/processed/classification_dataset.csv"


def remove_class_keywords(text):
    text = re.sub(r"\bfirst information report\b", " ", text, flags=re.I)
    text = re.sub(r"\bfir\b", " ", text, flags=re.I)
    text = re.sub(r"\bcharge sheet\b", " ", text, flags=re.I)
    text = re.sub(r"\bwitness statement\b", " ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


texts = []
labels = []
document_ids = []

with open(DATASET, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        texts.append(remove_class_keywords(row["text"]))
        labels.append(row["class_label"])
        document_ids.append(row["document_id"])


X_train, X_temp, y_train, y_temp = train_test_split(
    texts,
    labels,
    test_size=0.30,
    random_state=42,
    stratify=labels,
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp,
)


model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        ),
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            random_state=42,
        ),
    ),
])


model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("=" * 70)
print("KEYWORD ABLATION TEST")
print("=" * 70)

print(f"Test documents: {len(X_test)}")
print(f"Accuracy: {accuracy_score(y_test, predictions):.3f}")

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0,
    )
)

print("\nPredictions:")
for actual, predicted in zip(y_test, predictions):
    status = "✓" if actual == predicted else "✗"
    print(f"{status} Actual={actual:<20} Predicted={predicted}")

print("\nDone.")
