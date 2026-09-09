import csv
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


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


# --------------------------------------------------
# Recreate EXACT same split as train_baseline.py
# --------------------------------------------------

X_train, X_temp, y_train, y_temp, id_train, id_temp = train_test_split(
    texts,
    labels,
    document_ids,
    test_size=0.30,
    random_state=42,
    stratify=labels,
)

X_val, X_test, y_val, y_test, id_val, id_test = train_test_split(
    X_temp,
    y_temp,
    id_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp,
)


# --------------------------------------------------
# Build model
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
# Train ONLY on training set
# --------------------------------------------------

model.fit(X_train, y_train)


# --------------------------------------------------
# Evaluate held-out test set
# --------------------------------------------------

probabilities = model.predict_proba(X_test)
predictions = model.predict(X_test)

max_confidence = probabilities.max(axis=1)


print("=" * 70)
print("PROPER CONFIDENCE / REJECTION EVALUATION")
print("=" * 70)

print(f"Training documents : {len(X_train)}")
print(f"Validation documents: {len(X_val)}")
print(f"Test documents     : {len(X_test)}")


print("\nHELD-OUT TEST DOCUMENTS")
print("=" * 70)

for doc_id, actual, predicted, confidence in zip(
    id_test,
    y_test,
    predictions,
    max_confidence,
):
    correct = "✓" if actual == predicted else "✗"

    print(
        f"{correct} {doc_id:<22} "
        f"Actual={actual:<20} "
        f"Predicted={predicted:<20} "
        f"Confidence={confidence:.3f}"
    )


print("\nConfidence statistics on held-out test set")
print("=" * 70)
print(f"Minimum : {max_confidence.min():.3f}")
print(f"Maximum : {max_confidence.max():.3f}")
print(f"Average : {max_confidence.mean():.3f}")


# --------------------------------------------------
# Threshold analysis
# --------------------------------------------------

print("\nTHRESHOLD ANALYSIS")
print("=" * 70)

for threshold in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:

    accepted = max_confidence >= threshold

    accepted_count = accepted.sum()
    rejected_count = len(accepted) - accepted_count

    accepted_correct = sum(
        predicted == actual
        for predicted, actual, keep in zip(
            predictions,
            y_test,
            accepted,
        )
        if keep
    )

    accepted_accuracy = (
        accepted_correct / accepted_count
        if accepted_count > 0
        else 0
    )

    print(
        f"Threshold={threshold:.2f} | "
        f"Accepted={accepted_count:2d} | "
        f"Rejected={rejected_count:2d} | "
        f"Accuracy among accepted={accepted_accuracy:.3f}"
    )


# --------------------------------------------------
# Unsupported / out-of-domain examples
# --------------------------------------------------

unsupported_documents = {
    "invoice": """
    TAX INVOICE
    Invoice Number: INV-2026-1042
    Customer Name: ABC Traders
    Product Description: Computer Equipment
    Quantity: 5
    Total Amount: Rs. 85,000
    Payment Terms: Net 30 Days
    """,

    "leave_application": """
    APPLICATION FOR LEAVE

    To,
    The Principal

    Subject: Request for leave

    I request leave from 12 September to 15 September
    due to personal reasons.
    """,

    "meeting_notice": """
    MEETING NOTICE

    All department members are informed that a meeting
    will be held on Monday at 10:00 AM in Conference Room 2.

    Agenda:
    1. Project updates
    2. Upcoming deadlines
    3. Resource allocation
    """,

    "general_text": """
    The weather forecast indicates moderate rainfall
    across several regions during the next few days.
    """,
}


print("\nUNSUPPORTED / OUT-OF-DOMAIN TEST")
print("=" * 70)

for name, text in unsupported_documents.items():

    probs = model.predict_proba([text])[0]

    predicted_class = model.classes_[np.argmax(probs)]
    confidence = probs.max()

    print(
        f"{name:<20} "
        f"Raw prediction={predicted_class:<20} "
        f"Confidence={confidence:.3f}"
    )


print("\nDone.")
