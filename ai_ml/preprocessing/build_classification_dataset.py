import csv
import glob
import os
import re
from pypdf import PdfReader


FIR_OCR = "ai_ml/data/processed/ocr/fir_ocr.csv"

CHARGE_SHEET_DIR = "ai_ml/data/synthetic/charge_sheet"
WITNESS_DIR = "ai_ml/data/synthetic/witness_statement"

OUTPUT = "ai_ml/data/processed/classification_dataset.csv"


def clean_text(text):
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_pdf_text(path):
    """Extract text from a synthetic PDF."""
    try:
        reader = PdfReader(path)

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return clean_text(" ".join(pages))

    except Exception as e:
        print(f"ERROR reading {path}: {e}")
        return ""


rows = []


# --------------------------------------------------
# 1. FIR
# --------------------------------------------------

print("Loading FIR OCR...")

with open(FIR_OCR, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        text = clean_text(row["text"])

        rows.append({
            "document_id": row["document_id"],
            "class_label": "FIR",
            "text": text,
            "source": "FIR_Dataset_ICDAR2023",
        })


# --------------------------------------------------
# 2. Charge Sheets
# --------------------------------------------------

print("Extracting Charge Sheet text...")

charge_files = sorted(
    glob.glob(os.path.join(CHARGE_SHEET_DIR, "*.pdf"))
)

for path in charge_files:
    filename = os.path.basename(path)
    document_id = os.path.splitext(filename)[0]

    text = extract_pdf_text(path)

    rows.append({
        "document_id": document_id,
        "class_label": "Charge Sheet",
        "text": text,
        "source": "synthetic",
    })


# --------------------------------------------------
# 3. Witness Statements
# --------------------------------------------------

print("Extracting Witness Statement text...")

witness_files = sorted(
    glob.glob(os.path.join(WITNESS_DIR, "*.pdf"))
)

for path in witness_files:
    filename = os.path.basename(path)
    document_id = os.path.splitext(filename)[0]

    text = extract_pdf_text(path)

    rows.append({
        "document_id": document_id,
        "class_label": "Witness Statement",
        "text": text,
        "source": "synthetic",
    })


# --------------------------------------------------
# Save
# --------------------------------------------------

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "document_id",
            "class_label",
            "text",
            "source",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("CLASSIFICATION DATASET CREATED")
print("=" * 60)

print("Total documents:", len(rows))

for label in ["FIR", "Charge Sheet", "Witness Statement"]:
    count = sum(r["class_label"] == label for r in rows)
    empty = sum(
        r["class_label"] == label and len(r["text"]) == 0
        for r in rows
    )

    print(f"{label}: {count} documents | Empty text: {empty}")

print("\nSaved to:")
print(OUTPUT)
