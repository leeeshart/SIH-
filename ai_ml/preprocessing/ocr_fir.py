from PIL import Image
import pytesseract
import glob
import csv
import os
import re

INPUT_DIR = "ai_ml/data/raw/fir/icdar/FIR_images_v1"
OUTPUT_FILE = "ai_ml/data/processed/ocr/fir_ocr.csv"


def clean_text(text):
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Find FIR images
all_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.jpg")))

# Group images by police-station name
groups = {}

for path in all_files:
    filename = os.path.basename(path)

    if " PS" in filename:
        station = filename.split(" PS")[0]
    else:
        station = "Unknown"

    groups.setdefault(station, []).append(path)


# Select up to 3 FIRs from each station
files = []

for station in sorted(groups):
    files.extend(groups[station][:3])

# Keep exactly 30 for the first baseline experiment
files = files[:30]

print(f"Total FIR images available: {len(all_files)}")
print(f"Selected for OCR: {len(files)}")
print("\nStarting OCR...\n")

rows = []

for i, path in enumerate(files, 1):
    filename = os.path.basename(path)
    document_id = os.path.splitext(filename)[0]

    try:
        image = Image.open(path)

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        text = clean_text(text)

        rows.append({
            "document_id": document_id,
            "text": text,
            "char_count": len(text),
        })

        print(f"Processed {i}/{len(files)}: {filename}")

    except Exception as e:
        print(f"ERROR: {filename} -> {e}")

        rows.append({
            "document_id": document_id,
            "text": "",
            "char_count": 0,
        })


# Save OCR results
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["document_id", "text", "char_count"]
    )

    writer.writeheader()
    writer.writerows(rows)


print("\n" + "=" * 60)
print("OCR COMPLETE")
print("=" * 60)
print(f"Documents processed: {len(rows)}")
print(f"Saved to: {OUTPUT_FILE}")
