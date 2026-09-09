# AI/ML — Secure Digital Document Management System

This module provides the AI-based document classification and structural verification components for the SIH Secure Digital Document Management System.

## Overview

The current AI/ML prototype performs three main tasks:

1. OCR / text extraction from scanned documents
2. Document classification
3. Structural verification of Charge Sheets

The current supported document classes are:

- FIR
- Charge Sheet
- Witness Statement

`Other/Unknown` is intentionally not used as a trained class. Unsupported documents can instead be handled as an application-level review outcome when the classifier is not sufficiently confident.

---

## Pipeline

```text
Document
   ↓
OCR / Text Extraction
   ↓
Text Dataset
   ↓
TF-IDF Feature Extraction
   ↓
Logistic Regression Classifier
   ↓
Document Type + Confidence
   ↓
Structural Verification
   ↓
Verification Status
