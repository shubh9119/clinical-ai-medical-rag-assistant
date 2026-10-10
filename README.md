# Clinical AI Scribe, Multimodal Medical Imaging & Healthcare RAG Assistant

[![CI Pipeline](https://img.shields.io/badge/CI-Passing-brightgreen)](#)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](#)
[![FHIR R4](https://img.shields.io/badge/HL7-FHIR%20R4-red)](#)
[![Healthcare AI](https://img.shields.io/badge/Healthcare%20AI-HIPAA%20Aligned-teal)](#)

End-to-end **Healthcare AI Diagnostic & Ambient Clinical Scribe Platform** combining multimodal radiological image analysis (X-Ray, MRI, CT, Ultrasound) with structured **SOAP Note synthesis**, **ICD-10 medical coding extraction**, **HL7 FHIR R4 DiagnosticReport export**, and automated **clinical safety guardrails**.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Intake["Multimodal Clinical Intake"]
        IMG["Medical Imaging (X-Ray / MRI / CT / PNG)"]
        TRANSCRIPT["Patient-Clinician Consultation Transcript"]
    end

    subgraph Preproc["Normalization & PHI Sanitization"]
        NORM["16-Bit / RGBA Image Normalizer"]
        TEMP["Isolated Ephemeral Buffer"]
    end

    subgraph CoreAI["Clinical AI & Literature Grounding"]
        VLM["Multimodal Radiology Diagnostic Agent"]
        MEDRAG["PubMed & Clinical Guideline Retrieval"]
        SCRIBE["SOAP Note & ICD-10 NER Extractor"]
    end

    subgraph Guardrails["Safety & Interoperability"]
        SAFE["Automated Dosage & Contraindication Guardrail"]
        FHIR["HL7 FHIR R4 DiagnosticReport Builder"]
    end

    IMG --> NORM --> TEMP --> VLM
    TRANSCRIPT --> SCRIBE
    VLM --> MEDRAG --> SCRIBE
    SCRIBE --> SAFE --> FHIR
```

---

## Clinical Triage & Scribe Workflow

```mermaid
sequenceDiagram
    autonumber
    participant C as Clinician
    participant UI as Streamlit Clinical Portal
    participant A as Multimodal Medical Agent
    participant G as Safety & FHIR Guardrail Engine

    C->>UI: Upload medical scan + consultation context
    UI->>UI: Normalize color space (RGB/L) & aspect ratio in isolated temp file
    UI->>A: Execute structured radiological & differential analysis
    A->>A: Cross-reference clinical protocols & literature
    A-->>G: Output Findings + SOAP sections + ICD-10 candidates
    G->>G: Validate dosage bounds & extract ICD-10 codes
    G-->>C: Render Clinical Report + FHIR R4 JSON Bundle
```

---

## Key Bug Fixes & Production Hardening

1. **Concurrent Tempfile Isolation (`app.py`):** Replaced the hardcoded shared `"temp_resized_image.png"` buffer (which caused multi-user race conditions and leaked patient scan files on disk) with isolated `tempfile.NamedTemporaryFile` descriptors cleaned up inside a strict `finally:` block.
2. **16-Bit Grayscale & RGBA Medical Scan Normalization:** Added automatic color-space normalization (`image.convert("RGB")`) and zero-dimension guards prior to aspect-ratio resizing, preventing `OSError: cannot write mode RGBA/I;16` crashes on hospital PNG/DICOM exports.
3. **Null-Safe Agent Output & Initialization Guard:** Added explicit checks for uninitialized agent state and empty/filtered `RunOutput.content` responses.
4. **HL7 FHIR R4 & Safety Guardrails (`clinical_scribe.py`):** Implemented deterministic ICD-10 regex NER extraction, unsafe dosage regex guardrails, and HL7 FHIR R4 `DiagnosticReport` serialization.

---

## Quickstart

```bash
git clone https://github.com/shubh9119/clinical-ai-medical-rag-assistant.git
cd clinical-ai-medical-rag-assistant
pip install -r requirements.txt
streamlit run app.py
```

### Run Unit Tests
```bash
pytest -v
```
