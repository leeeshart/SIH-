# Secure Digital Document Management & Verification System

A secure digital document management system for police and legal workflows, designed to improve document organization, verification, traceability, and tamper-evident record keeping.

## Problem Statement

Police and legal departments handle large volumes of sensitive documents such as FIRs, charge sheets, witness statements, and investigation records.

Traditional document workflows can make it difficult to:

- Organize and retrieve documents efficiently
- Verify whether documents follow the expected structure
- Track document versions and modifications
- Detect unauthorized or unexpected changes
- Maintain a reliable audit history
- Protect sensitive legal and investigation documents

This project proposes a centralized digital system combining secure storage, role-based access control, AI-assisted document analysis, cryptographic hashing, and blockchain-based tamper-evident records.

---

## System Overview

The system follows this high-level workflow:

```text
                    ┌──────────────────┐
                    │      User        │
                    │ Police / Legal   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Frontend      │
                    │ Login / Upload   │
                    │ Search / View    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌────────────┐ ┌─────────────┐ ┌──────────────┐
       │    RBAC    │ │  Document   │ │   AI / ML    │
       │ Permissions│ │   Service   │ │ Classification│
       └────────────┘ └─────────────┘ │ Verification │
                                      └───────┬──────┘
                                              │
                    ┌─────────────────────────┼────────────────────┐
                    │                         │                    │
                    ▼                         ▼                    ▼
             ┌─────────────┐          ┌─────────────┐       ┌─────────────┐
             │ PostgreSQL  │          │   Secure    │       │ Blockchain  │
             │ Metadata /  │          │   Storage   │       │ SHA-256 +   │
             │ Audit Data  │          │  Encrypted  │       │  Metadata   │
             └─────────────┘          └─────────────┘       └─────────────┘
```

## Core Features
### 1. Secure Authentication & Role-Based Access Control

The system restricts document operations according to the user's role.

Examples of controlled operations include:

- Uploading documents
- Viewing documents
- Modifying documents
- Sharing documents
- Managing document records

RBAC controls who is allowed to perform an action. It does not determine whether a document itself is authentic.


### 2. Digital Document Management

The document service manages the document lifecycle, including:

- Upload
- Storage
- Retrieval
- Versioning
- Document metadata
- Status tracking
- AI processing
- Audit events

Each document can have multiple versions while maintaining a traceable history.

### 3. AI-Based Document Classification

The AI/ML module identifies the type of uploaded document.

The current prototype supports:

FIR
Charge Sheet
Witness Statement

The classification pipeline uses OCR/text extraction followed by machine-learning classification.

### Current baseline:

```text

Document
   ↓
OCR / Text Extraction
   ↓
Text Preprocessing
   ↓
TF-IDF Features
   ↓
Logistic Regression
   ↓
Document Type + Confidence

```

### 4. AI-Assisted Structural Verification

After classification, the document is checked for expected structural elements.

For example, the Charge Sheet verification module checks for:

- Form title
- FIR details
- Court information
- Acts and sections
- Accused information
- Witness information
- Brief facts
- Signature information

The verification result can be:

```text
CONFORMS
NEEDS REVIEW
DOES NOT CONFORM

```

This is a structural conformity check. It does not determine whether a document is legally genuine or fake.

For more details about the AI/ML implementation, see ai_ml/README.md.

## Security & Integrity
### 5. Cryptographic Hashing

A SHA-256 hash is generated from the original document.

```text

Original Document
       ↓
    SHA-256
       ↓
Document Hash

```

The hash acts as a unique cryptographic fingerprint of the document.

If the document content is modified, its hash changes, allowing the system to detect a mismatch.

### 6. Blockchain-Based Tamper-Evident Records

The document hash and relevant metadata can be recorded on the blockchain.

Stored information may include:

- Document ID
- Version
- SHA-256 hash
- Timestamp
- Authorized actor

Blockchain provides a tamper-evident history of document records.

It does not prevent someone from modifying the original document. Instead, it helps detect whether the current document differs from the previously recorded version.

### 7. Encrypted Storage

The original document is stored separately in encrypted storage.

This provides confidentiality for sensitive police and legal documents.

The different security layers have different purposes:

```text


RBAC
 ↓
Controls WHO can access the document

Encryption
 ↓
Protects WHAT the document contains

SHA-256
 ↓
Detects changes to the document

Blockchain
 ↓
Maintains a tamper-evident record of the hash/history

Audit Logs
 ↓
Records WHO did WHAT and WHEN\

```

### 8. Audit Logging

Important actions performed on documents are recorded in an audit trail.

Examples include:

- Document upload
- Document viewing
- Document modification
- Document sharing
- New document version
- AI processing
- Verification events

This provides traceability throughout the document lifecycle.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React / Next.js |
| Backend | FastAPI / Python |
| AI/ML | Python, scikit-learn, OCR, OpenCV / Pillow |
| Database | PostgreSQL |
| Document Storage | Encrypted Secure Storage |
| Integrity | SHA-256 |
| Tamper-Evident Layer | Blockchain / Smart Contract |
| Access Control | Role-Based Access Control (RBAC) |
| Document Processing | PDF Processing + OCR |


### Project Structure

```text

SIH-/
│
├── frontend/
│   └── ...
│
├── backend/
│   └── ...
│
├── ai_ml/
│   ├── data/
│   ├── preprocessing/
│   ├── classification/
│   ├── verification/
│   ├── requirements.txt
│   └── README.md
│
├── .gitignore
└── README.md

```

## AI/ML Module

The AI/ML implementation is contained inside:

```text

ai_ml/
├── preprocessing/
│   ├── ocr_fir.py
│   └── build_classification_dataset.py
│
├── classification/
│   ├── train_baseline.py
│   ├── test_confidence.py
│   └── evaluation/
│       ├── test_rejection.py
│       └── test_keyword_ablation.py
│
└── verification/
    └── verify_charge_sheet.py

```

The AI/ML module currently focuses on:

- OCR and text extraction
- Document classification
- Classification evaluation
- Structural verification

See ai_ml/README.md for the detailed AI/ML pipeline, dataset information, experiments, and results.

## Prototype Results

The current AI/ML implementation has been tested as a proof of concept.

### Classification

Using a TF-IDF + Logistic Regression baseline:

- Validation accuracy: 100%
- Test accuracy: 100% (14/14)
- FIR: 5/5
- Charge Sheet: 4/4
- Witness Statement: 5/5

### OCR

A pilot test was performed on 30 FIR images:

- 30/30 produced non-empty OCR output
- Mean extracted text: approximately 1,758 characters/document
- Median extracted text: approximately 1,745 characters/document


### Structural Verification

The Charge Sheet verification prototype detected:

- 8/8 required elements on valid samples
- A deliberately damaged document triggered NEEDS REVIEW

These results come from a small proof-of-concept dataset. They demonstrate that the pipeline works end-to-end and should not be interpreted as production-level accuracy.

## Dataset & Privacy

The project uses public/reference material and synthetic data for prototyping.

Sensitive documents and personally identifiable information are not intended to be committed to this repository.

The AI/ML data directory is organized as:

```text

ai_ml/data/
├── raw/              # Local/restricted datasets
├── processed/        # Locally generated processed data
├── reference_only/   # Reference documents/templates
├── manifests/        # Dataset metadata and provenance
└── synthetic/        # Locally generated synthetic documents


```


Raw datasets, processed datasets, synthetic generated documents, and trained model files are excluded from version control where appropriate.

For real police or legal documents, authorization, privacy requirements, and data licensing must be established before using them for training or evaluation.

## Current Limitations

This is currently a proof-of-concept implementation.

### Some important limitations are:

- Small training and evaluation dataset
- Synthetic documents do not fully represent real operational documents
- OCR performance can vary depending on scan and image quality
- Police document formats can vary across jurisdictions and time
- Similar templates can introduce dataset leakage
- Confidence scores alone are not sufficient for reliable open-set document rejection
- Structural verification is not forensic document authentication
- Further evaluation on diverse and authorized real-world documents is required


## Future Improvements

Planned or possible improvements include:

- Larger and more diverse datasets
- Improved OCR and handwriting recognition
- Layout-aware document models
- Multimodal classification using text, layout, and visual features
- More reliable open-set document detection
- Visual and structural anomaly detection
- Document version comparison
- Change highlighting between document versions
- Human-in-the-loop review for uncertain AI results
- Integration with the complete frontend and backend
- Evaluation on authorized real-world documents

  
## Disclaimer

This project is a research and hackathon prototype.

The AI system is designed to assist authorized users with document classification and structural checking. AI results should not replace legal judgment, forensic examination, or official verification procedures.

The system does not claim that a document is legally authentic or fraudulent based solely on AI output.


## References

1. **Smart India Hackathon 2026 — Problem Statement 26190**  
   Secure Digital Document Management System for Legal and Investigation Documents, Ministry of Home Affairs.  
   https://sih.gov.in/

2. **Chakraborty, S., Harit, G., & Ghosh, S. (2023).**  
   *TransDocAnalyser: A Framework for Offline Semi-structured Handwritten Document Analysis in the Legal Domain.*  
   Proceedings of the 17th International Conference on Document Analysis and Recognition (ICDAR).  
   https://www.researchgate.net/publication/373227561_TransDocAnalyser_A_Framework_for_Semi-structured_Offline_Handwritten_Documents_Analysis_with_an_Application_to_Legal_Domain

3. **FIR_Dataset_ICDAR2023 — LegalDocumentProcessing.**  
   Indian FIR document dataset containing handwritten and printed documents with field-level annotations.  
   https://github.com/LegalDocumentProcessing/FIR_Dataset_ICDAR2023

4. **Puducherry Police — FORM IF5.**  
   Official police form for Final Form / Report.  
   https://police.py.gov.in/Police%20manual/Forms%20pdf/FORM-%20IF5.pdf

5. **Puducherry Police — Police Manual Volume III: Forms.**  
   Official police forms reference, including Integrated Forms IF1–IF7.  
   https://police.py.gov.in/Police%20manual/Police%20Manual%20Volume%20III%20with%20Forms.htm

6. **Government of Puducherry — BNSS 2023 Notification.**  
   Notification updating the Final Form / Report reference from Section 173 CrPC to Section 193 BNSS.  
   https://styandptg.py.gov.in/2024/OCTOBER/EXTRAORDINARYPART-I/139-PART-I%20dated%2021-10-2024.pdf

7. **Maharashtra Police — FORM IF5 under BNSS 2023.**  
   Official example of the updated IF5 Final Form / Report format.  
   https://www.mahapolice.gov.in/uploads/d090e8a4ec7bdad9ba2a23d615c4cfc1.pdf

This fits **exactly after the section you already wrote** and keeps the root README as the overview, while the `ai_ml/README.md` remains the technical deep dive.
