import re
import sys
from pathlib import Path

from pypdf import PdfReader


# --------------------------------------------------
# Expected structural elements
# --------------------------------------------------

REQUIRED_ELEMENTS = {
    "form_title": [
        r"\bFORM\s*IF5\b",
        r"\bFINAL\s+FORM\b",
        r"\bFINAL\s+FORM\s*/\s*REPORT\b",
    ],

    "fir_details": [
        r"\bFIR\b",
        r"\bFIR\s*(NO|NUMBER)\b",
    ],

    "court_information": [
        r"\bCOURT\b",
    ],

    "acts_sections": [
        r"\bACTS?\b",
        r"\bSECTIONS?\b",
    ],

    "accused_details": [
        r"\bACCUSED\b",
    ],

    "witness_details": [
        r"\bWITNESS(?:ES)?\b",
    ],

    "brief_facts": [
        r"\bBRIEF\s+FACTS\b",
    ],

    "signature_section": [
        r"\bSIGNATURE\b",
        r"\bSHO\b",
        r"\bINVESTIGATING\s+OFFICER\b",
    ],
}


# --------------------------------------------------
# Extract PDF text
# --------------------------------------------------

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


# --------------------------------------------------
# Check one structural element
# --------------------------------------------------

def check_element(text, patterns):

    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


# --------------------------------------------------
# Verify Charge Sheet
# --------------------------------------------------

def verify_charge_sheet(pdf_path):

    text = extract_text(pdf_path)

    results = {}

    for element, patterns in REQUIRED_ELEMENTS.items():
        results[element] = check_element(text, patterns)

    passed = sum(results.values())
    total = len(results)

    if passed == total:
        status = "CONFORMS"

    elif passed >= total * 0.70:
        status = "NEEDS REVIEW"

    else:
        status = "DOES NOT CONFORM"

    return status, results, passed, total


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("python ai_ml/verification/verify_charge_sheet.py <pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    status, results, passed, total = verify_charge_sheet(pdf_path)

    print("=" * 65)
    print("CHARGE SHEET STRUCTURAL VERIFICATION")
    print("=" * 65)

    print(f"\nDocument: {pdf_path.name}")

    print("\nStructural checks:")
    print("-" * 65)

    for element, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"{symbol} {element.replace('_', ' ').title()}")

    print("\n" + "-" * 65)
    print(f"Checks passed: {passed}/{total}")
    print(f"Verification status: {status}")

    print("\nNote:")
    print(
        "This verifies structural conformity only. "
        "It does not determine legal authenticity or whether "
        "a document is genuine/fake."
    )