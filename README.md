# 🧠 Clinical NLP Extractor

The **Clinical NLP Extractor** is a Streamlit-based application that automatically extracts structured medical data — such as **clinical terms, diagnoses, anatomical locations, procedures, and medical codes** — from multi-report clinical PDF documents.

---

## 🚀 Features

- 📄 **PDF Text Extraction:** Reads multi-report clinical PDFs using `PyMuPDF (fitz)`.
- 🧬 **Clinical NLP Matching:** Identifies key terms, anatomical locations, diagnoses, and procedures using predefined medical dictionaries.
- ⚕️ **Medical Code Mapping:** Automatically associates each report with its corresponding ICD-10, CPT, and HCPCS codes.
- 🧾 **Multi-Report Handling:** Supports PDFs containing multiple reports (e.g., “Report 1”, “Report 2”, etc.).
- 💾 **JSON Export:** Download the extracted structured data in JSON format for further analysis or integration.
- 🖥️ **Interactive UI:** Built with Streamlit for easy use and instant feedback.

---

## 🧩 Tech Stack

- **Language:** Python 3.x  
- **Framework:** Streamlit  
- **Libraries:**  
  - `fitz (PyMuPDF)` → PDF text extraction  
  - `re` → Regular expressions for text parsing  
  - `json` → Structured output serialization  
  - `collections.defaultdict` → Simplified data organization  

---

## 🧰 Installation

### 1. Clone this repository

git clone https://github.com/yourusername/clinical-nlp-extractor.git
cd clinical-nlp-extractor
### 2. Run in respective folder
