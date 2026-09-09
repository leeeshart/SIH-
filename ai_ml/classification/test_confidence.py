import pandas as pd
import joblib

MODEL_PATH = "ai_ml/models/tfidf_logistic_baseline.joblib"
DATA_PATH = "ai_ml/data/processed/classification_dataset.csv"

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

X = df["text"].fillna("")

probabilities = model.predict_proba(X)
predictions = model.predict(X)

print("\nCONFIDENCE TEST")
print("=" * 60)

for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
    confidence = probs.max()
    actual = df.iloc[i]["class_label"]

    print(
        f"{df.iloc[i]['document_id']:<20} "
        f"Actual={actual:<20} "
        f"Predicted={pred:<20} "
        f"Confidence={confidence:.3f}"
    )

print("\nConfidence statistics")
print("=" * 60)
print(f"Minimum: {probabilities.max(axis=1).min():.3f}")
print(f"Maximum: {probabilities.max(axis=1).max():.3f}")
print(f"Average: {probabilities.max(axis=1).mean():.3f}")
