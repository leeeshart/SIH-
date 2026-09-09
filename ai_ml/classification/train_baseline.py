import csv
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


DATASET = "ai_ml/data/processed/classification_dataset.csv"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

texts = []
labels = []
document_ids = []

with open(DATASET, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        texts.append(row["text"])
        labels.append(row["class_label"])
        document_ids.append(row["document_id"])


print("=" * 60)
print("TF-IDF + LOGISTIC REGRESSION BASELINE")
print("=" * 60)

print(f"Total documents: {len(texts)}")


# --------------------------------------------------
# Train / validation / test split
# --------------------------------------------------

# First: 70% train, 30% temporary
X_train, X_temp, y_train, y_temp, id_train, id_temp = train_test_split(
    texts,
    labels,
    document_ids,
    test_size=0.30,
    random_state=42,
    stratify=labels,
)

# Split temporary 50/50 -> 15% validation, 15% test
X_val, X_test, y_val, y_test, id_val, id_test = train_test_split(
    X_temp,
    y_temp,
    id_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp,
)


print("\nSplit:")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Test:", len(X_test))


# --------------------------------------------------
# TF-IDF + Logistic Regression
# --------------------------------------------------

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


# --------------------------------------------------
# Train
# --------------------------------------------------

print("\nTraining model...")

model.fit(X_train, y_train)


# --------------------------------------------------
# Validation
# --------------------------------------------------

val_predictions = model.predict(X_val)

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print("Accuracy:", round(
    accuracy_score(y_val, val_predictions), 4
))

print("\nClassification report:")
print(
    classification_report(
        y_val,
        val_predictions,
        zero_division=0,
    )
)


# --------------------------------------------------
# Final test
# --------------------------------------------------

test_predictions = model.predict(X_test)

print("\n" + "=" * 60)
print("TEST RESULTS")
print("=" * 60)

print("Accuracy:", round(
    accuracy_score(y_test, test_predictions), 4
))

print("\nClassification report:")
print(
    classification_report(
        y_test,
        test_predictions,
        zero_division=0,
    )
)


# --------------------------------------------------
# Confusion matrix
# --------------------------------------------------

classes = [
    "FIR",
    "Charge Sheet",
    "Witness Statement",
]

cm = confusion_matrix(
    y_test,
    test_predictions,
    labels=classes,
)

print("\nConfusion Matrix")
print("Rows = Actual")
print("Columns = Predicted\n")

print("                  FIR  Charge  Witness")

for label, row in zip(classes, cm):
    print(f"{label:18}", *row)


# --------------------------------------------------
# Show predictions
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEST PREDICTIONS")
print("=" * 60)

for doc_id, actual, predicted in zip(
    id_test,
    y_test,
    test_predictions,
):
    status = "✓" if actual == predicted else "✗"

    print(
        f"{status} {doc_id} | "
        f"Actual: {actual} | "
        f"Predicted: {predicted}"
    )


# --------------------------------------------------
# Save model
# --------------------------------------------------

try:
    import joblib

    os.makedirs("ai_ml/models", exist_ok=True)

    model_path = "ai_ml/models/tfidf_logistic_baseline.joblib"

    joblib.dump(model, model_path)

    print("\nModel saved to:")
    print(model_path)

except ImportError:
    print("\njoblib not installed; model was not saved.")


print("\nDone.")
