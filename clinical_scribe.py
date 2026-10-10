"""Clinical AI Scribe & FHIR R4 / SOAP Note Generator with Medical Safety Guardrails."""
import re
from datetime import datetime, timezone
from typing import Dict, List, Any

ICD10_PATTERN = re.compile(r"\b([A-TV-Z][0-9][0-9AB](?:\.[0-9A-TV-Z]{1,4})?)\b")
UNSAFE_DOSAGE_PATTERNS = [
    re.compile(r"\b(\d{4,})\s*mg\b", re.IGNORECASE),
    re.compile(r"discontinue\s+all\s+medications\s+immediately", re.IGNORECASE),
]

def extract_icd10_codes(clinical_text: str) -> List[str]:
    """Extract unique ICD-10 diagnostic codes from clinical notes."""
    if not clinical_text:
        return []
    seen = []
    for match in ICD10_PATTERN.findall(clinical_text):
        if match not in seen:
            seen.append(match)
    return seen

def validate_clinical_safety(note_text: str) -> Dict[str, Any]:
    """Run automated clinical safety guardrails on generated medical notes."""
    flags = []
    for pat in UNSAFE_DOSAGE_PATTERNS:
        if pat.search(note_text or ""):
            flags.append(f"Triggered safety rule: {pat.pattern}")
    return {
        "passed": len(flags) == 0,
        "flags": flags,
        "requires_physician_signoff": True,
    }

def build_fhir_r4_diagnostic_report(
    patient_id: str,
    subjective: str,
    objective: str,
    assessment: str,
    plan: str,
) -> Dict[str, Any]:
    """Convert structured SOAP note sections into a HIPAA-aligned HL7 FHIR R4 DiagnosticReport resource."""
    if not patient_id or not patient_id.strip():
        raise ValueError("patient_id is required for FHIR resource generation")
    full_text = f"{subjective} {objective} {assessment} {plan}"
    icd_codes = extract_icd10_codes(full_text)
    safety = validate_clinical_safety(full_text)
    return {
        "resourceType": "DiagnosticReport",
        "status": "preliminary" if safety["requires_physician_signoff"] else "final",
        "subject": {"reference": f"Patient/{patient_id.strip()}"},
        "issued": datetime.now(timezone.utc).isoformat(),
        "conclusion": assessment.strip(),
        "conclusionCode": [
            {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": code,
                    }
                ]
            }
            for code in icd_codes
        ],
        "extension": [
            {
                "url": "https://clinical-ai.local/fhir/StructureDefinition/soap-note",
                "valueString": f"S: {subjective} | O: {objective} | A: {assessment} | P: {plan}",
            },
            {
                "url": "https://clinical-ai.local/fhir/StructureDefinition/safety-guardrail",
                "valueBoolean": safety["passed"],
            },
        ],
    }
