import io
import os
import re
import tempfile
from pathlib import Path

import joblib
import pytesseract
from PIL import Image
from fastapi import FastAPI, File, HTTPException, UploadFile

from ai_ml.verification.verify_charge_sheet import (
    extract_text,
    verify_charge_sheet,
)


# Project root: /workspaces/SIH-
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ai_ml"
    / "models"
    / "tfidf_logistic_baseline.joblib"
)


app = FastAPI(
    title="SIH Document AI/ML API",
    description="Document classification and structural verification API",
    version="1.0.0",
)


# Load the trained model once when the API starts
if not MODEL_PATH.exists():
    raise RuntimeError(f"Model not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)


def clean_text(text: str) -> str:
    """Normalize extracted OCR/text content."""
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_upload(filename: str, raw_bytes: bytes):
    """Extract text from PDF or image uploads."""

    lower = filename.lower()

    # PDF
    if lower.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as tmp:
            tmp.write(raw_bytes)
            tmp_path = tmp.name

        text = extract_text(tmp_path)
        return text, tmp_path

    # Image
    if lower.endswith((".jpg", ".jpeg", ".png")):
        try:
            image = Image.open(io.BytesIO(raw_bytes))

            text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            )

            return clean_text(text), None

        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Could not process image: {exc}"
            )

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Use PDF, JPG, or PNG."
    )


@app.get("/")
def root():
    return {
        "service": "SIH Document AI/ML API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "tfidf_logistic_baseline"
    }


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):
    """Classify an uploaded document and optionally verify Charge Sheets."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    raw_bytes = await file.read()

    if not raw_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    tmp_pdf_path = None

    try:
        text, tmp_pdf_path = extract_text_from_upload(
            file.filename,
            raw_bytes
        )

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this document."
            )

        # Classification
        predicted_class = model.predict([text])[0]

        probabilities = model.predict_proba([text])[0]

        confidence = dict(
            zip(
                model.classes_,
                probabilities.tolist()
            )
        )

        response = {
            "filename": file.filename,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "verification": None,
        }

        # Charge Sheet structural verification
        if predicted_class == "Charge Sheet" and tmp_pdf_path:
            status, results, passed, total = verify_charge_sheet(
                tmp_pdf_path
            )

            response["verification"] = {
                "status": status,
                "checks_passed": passed,
                "checks_total": total,
                "elements": results,
            }

        return response

    finally:
        # Delete temporary uploaded PDF after processing
        if tmp_pdf_path and os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)


@app.post("/verify-charge-sheet")
async def verify_charge_sheet_document(
    file: UploadFile = File(...)
):
    """Verify the structural conformity of a Charge Sheet PDF."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Charge Sheet verification currently supports PDF files only."
        )

    raw_bytes = await file.read()

    if not raw_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    tmp_pdf_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as tmp:
            tmp.write(raw_bytes)
            tmp_pdf_path = tmp.name

        status, results, passed, total = verify_charge_sheet(
            tmp_pdf_path
        )

        return {
            "filename": file.filename,
            "verification": {
                "status": status,
                "checks_passed": passed,
                "checks_total": total,
                "elements": results,
            },
        }

    finally:
        if tmp_pdf_path and os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)
