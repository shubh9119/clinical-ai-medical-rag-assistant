import pytest
from clinical_scribe import extract_icd10_codes, validate_clinical_safety, build_fhir_r4_diagnostic_report

def test_extract_icd10_codes_deduplicates():
    note = "Assessment: Type 2 diabetes mellitus (E11.9) and essential hypertension (I10). Confirmed E11.9."
    assert extract_icd10_codes(note) == ["E11.9", "I10"]

def test_validate_clinical_safety_catches_extreme_dosage():
    unsafe_note = "Administer 5000 mg of metoprolol orally."
    res = validate_clinical_safety(unsafe_note)
    assert res["passed"] is False
    assert len(res["flags"]) == 1

def test_build_fhir_r4_diagnostic_report_structure():
    report = build_fhir_r4_diagnostic_report(
        patient_id="pat-9021",
        subjective="Patient reports mild shortness of breath.",
        objective="Chest X-ray clear; SpO2 98%.",
        assessment="Acute bronchitis (J20.9).",
        plan="Supportive care and hydration.",
    )
    assert report["resourceType"] == "DiagnosticReport"
    assert report["subject"]["reference"] == "Patient/pat-9021"
    assert report["conclusionCode"][0]["coding"][0]["code"] == "J20.9"
