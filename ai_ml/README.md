# AI/ML Module — Document Classification & Verification

Part of the SIH 2026 Secure Digital Document Management System (Problem Statement 26190).
Handles document classification (what type of document) and structural verification
(does it conform to the expected format) for legal/investigation documents.

## Pipeline

1. **OCR** — `preprocessing/ocr_fir.py`: OCRs a sample of FIR images (≤3 per police
   station, 30 total) into text → `data/processed/ocr/fir_ocr.csv`.
2. **Dataset build** — `preprocessing/build_classification_dataset.py`: combines FIR OCR
   text with extracted text from synthetic Charge Sheet and Witness Statement PDFs into
   `data/processed/classification_dataset.csv`.
3. **Baseline model** — `classification/train_baseline.py`: TF-IDF + Logistic Regression,
   stratified 70/15/15 train/val/test split.
4. **Evaluation**
   - `classification/test_confidence.py` — confidence scores across the full dataset.
   - `classification/evaluation/test_rejection.py` — confidence-threshold rejection
     analysis on the held-out test set, plus an out-of-domain test (invoice, leave
     application, meeting notice, generic text).
   - `classification/evaluation/test_keyword_ablation.py` — strips obvious class-name
     keywords ("FIR", "charge sheet", "witness statement") to confirm the model isn't
     just matching label names.
5. **Verification** — `verification/verify_charge_sheet.py`: checks 8 required structural
   elements (form title, FIR details, court info, acts/sections, accused, witness, brief
   facts, signature) and returns CONFORMS / NEEDS REVIEW / DOES NOT CONFORM.

## Design notes

- 3-class classification (FIR, Charge Sheet, Witness Statement) — no trained
  "Other/Unknown" class. Out-of-domain documents are instead caught via low
  classification confidence, since a synthetic catch-all class would be an incoherent
  document type rather than a real fourth category.
- Verification is a structural-conformity check (presence/absence of required text
  fields), not a visual or forensic authenticity check — it does not claim to determine
  whether a document is genuine or fake.

## How to run

Order matters — each script depends on the previous step's output.

    python ai_ml/preprocessing/ocr_fir.py
    python ai_ml/preprocessing/build_classification_dataset.py
    python ai_ml/classification/train_baseline.py
    python ai_ml/classification/test_confidence.py
    python ai_ml/classification/evaluation/test_rejection.py
    python ai_ml/classification/evaluation/test_keyword_ablation.py
    python ai_ml/verification/verify_charge_sheet.py <path-to-pdf>

## Results (POC dataset)

**Classification** (TF-IDF + Logistic Regression)
- Validation accuracy: 100%
- Test accuracy: 100% (14/14) — FIR 5/5, Charge Sheet 4/4, Witness Statement 5/5

**OCR pilot**
- 30 FIR images → 30/30 non-empty OCR outputs
- Mean ≈ 1,758 chars/document, median ≈ 1,745

**Verification**
- Valid Charge Sheet → 8/8, CONFORMS
- Damaged Charge Sheet (one required element removed) → 7/8, NEEDS REVIEW

Note: this is a small POC dataset (14 test documents) — these numbers demonstrate the
pipeline works end-to-end, not production-level accuracy.
