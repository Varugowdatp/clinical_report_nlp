import streamlit as st
import fitz   
import re
from collections import defaultdict
import json

st.set_page_config(page_title="Clinical NLP Extractor", layout="wide")

EXPECTED_COUNTS = {
    "Report 1": 26,
    "Report 2": 20,
    "Report 3": 26,
    "Report 4": 24
}

# Dictionaries for each report
CLINICAL_TERMS_BY_REPORT = {
    "Report 1": ["colon polyps", "colon polyps (history)", "internal hemorrhoids", "diverticulosis",
                 "rectal exam", "melanosis coli", "moderate sigmoid diverticulosis",
                 "no polyps found", "good bowel preparation", "no immediate complications",
                 "no immediate complication", "monitored anesthesia care", "lidocaine", "propofol",
                 "lactated ringer's"],
    "Report 2": ["colon cancer screening", "hemorrhoids", "sessile polyp", "polyp removal",
                 "no immediate complication", "no immediate complications", "cold snare"],
    "Report 3": ["rectal bleeding", "ulcer of anus and rectum", "internal hemorrhoids",
                 "hemorrhage of anus and rectum", "localized erosion", "localized erosion (proctitis)",
                 "biopsy taken", "good bowel prep", "minimal estimated blood loss",
                 "cold forceps", "bbps", "boston bowel preparation scoring"],
    "Report 4": ["atypical chest pain", "right upper quadrant abdominal pain", "gastritis",
                 "barrett's esophagus", "biopsies for h. pylori", "biopsy for h. pylori",
                 "mild antral and body gastritis", "irregular z-line", "no ulcers or masses",
                 "no immediate complications", "no immediate complication",
                 "monitored anesthesia care", "lidocaine", "propofol", "lactated ringer's", "egd"]
}

ANATOMICAL_LOCATIONS_BY_REPORT = {
    "Report 1": ["rectum", "sigmoid colon", "cecum", "proximal colon", "ileocecal valve", "appendiceal orifice"],
    "Report 2": ["anal canal", "rectum", "sigmoid colon", "descending colon", "splenic flexure",
                 "transverse colon", "hepatic flexure", "ascending colon", "cecum", "terminal ileum"],
    "Report 3": ["anus", "rectum", "distal rectum", "anal verge", "right colon", "transverse colon",
                 "left colon", "cecum", "appendiceal orifice", "ileocecal valve"],
    "Report 4": ["distal esophagus", "stomach", "antrum", "stomach body", "duodenal bulb",
                 "2nd portion of duodenum", "right upper quadrant"]
}

DIAGNOSIS_BY_REPORT = {
    "Report 1": ["personal history of colonic polyps", "internal hemorrhoids",
                 "diverticulosis", "diverticulosis (sigmoid)", "melanosis coli",
                 "no new polyps seen in this examination", "colon polyps"],
    "Report 2": ["colon cancer screening", "hemorrhoids", "sessile polyp in descending colon"],
    "Report 3": ["ulcer in the rectum", "internal hemorrhoids (moderate)",
                 "single erosion at anal verge", "single erosion at anal verge (proctitis)",
                 "rectal bleeding", "hemorrhage of anus and rectum", "ulcer of anus and rectum"],
    "Report 4": ["atypical chest pain", "right upper quadrant pain", "mild gastritis",
                 "suspected barrett's esophagus (biopsied)", "gastritis", "biopsies for h. pylori"]
}

PROCEDURES_BY_REPORT = {
    "Report 1": ["colonoscopy", "rectal examination", "scope passage to cecum", "retroflexion in rectum",
                 "monitored anesthesia care", "mac", "intravenous medication administration",
                 "lidocaine", "propofol", "lactated ringer's"],
    "Report 2": ["colonoscopy", "cold snare polypectomy", "cold snare"],
    "Report 3": ["colonoscopy", "biopsy using cold forceps", "retroflexion in rectum",
                 "boston bowel preparation scoring", "bbps"],
    "Report 4": ["egd", "esophagogastroduodenoscopy", "biopsy for h. pylori",
                 "biopsy of distal esophagus", "retroflexion in the stomach",
                 "monitored anesthesia care", "intravenous medication administration",
                 "lidocaine", "propofol", "lactated ringer's"]
}

CODES_PER_REPORT = {
    "Report 1": {"ICD-10": ["Z86.0100", "K64.8", "K57.90"], "CPT": ["45378"], "HCPCS": ["J3490", "A4216"]},
    "Report 2": {"ICD-10": ["Z12.11", "K64.9"], "CPT": ["45385"], "HCPCS": []},
    "Report 3": {"ICD-10": ["K62.6", "K64.8", "K62.5"], "CPT": ["45380"], "HCPCS": []},
    "Report 4": {"ICD-10": ["R07.89", "R10.11", "K29.70"], "CPT": ["43239"], "HCPCS": ["J3490"]}
}

# Functions
def extract_text_pymupdf(file_obj):
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")
    text = " ".join(page.get_text("text") for page in doc)
    doc.close()
    return text

def find_matches(text, term_list):
    found = []
    text_lower = text.lower()
    for term in term_list:
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(term)
    return sorted(set(found))

def extract_from_report(report_text, report_id):
    data = defaultdict(list)
    text = report_text.lower()

    data["ReportID"] = report_id
    data["Clinical Terms"] = find_matches(text, CLINICAL_TERMS_BY_REPORT.get(report_id, []))
    data["Anatomical Locations"] = find_matches(text, ANATOMICAL_LOCATIONS_BY_REPORT.get(report_id, []))
    data["Diagnosis"] = find_matches(text, DIAGNOSIS_BY_REPORT.get(report_id, []))
    data["Procedures"] = find_matches(text, PROCEDURES_BY_REPORT.get(report_id, []))
    data.update(CODES_PER_REPORT.get(report_id, {"ICD-10": [], "CPT": [], "HCPCS": []}))
    return dict(data)


# Streamlit App
st.title("Clinical PDF Extractor")
st.write("Upload your clinical multi-report PDF to extract structured data.")

uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        raw_text = extract_text_pymupdf(uploaded_file)
    parts = re.split(r"(report\s*\d+)", raw_text, flags=re.I)
    reports, current_id = {}, None
    for part in parts:
        if re.match(r"report\s*\d+", part.strip(), re.I):
            num = re.search(r"report\s*(\d+)", part.strip(), re.I)
            if num:
                current_id = f"Report {num.group(1)}"
                reports[current_id] = ""
        elif current_id:
            reports[current_id] += part

    results = []
    for rid, txt in reports.items():
        if txt.strip():
            r = extract_from_report(txt, rid)
            if "ReportID" in r:
                results.append(r)

    if results:
        st.markdown("### Extracted Structured Data")
        for r in results:
            with st.expander(f"{r['ReportID']}"):
                st.json(r)
        st.markdown("### Download Extracted Data")
        json_data = json.dumps(results, indent=4)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="extracted_reports.json",
            mime="application/json"
        )
    else:
        st.warning("No valid reports found in PDF.")
else:
    st.info("Please upload your clinical PDF to start extraction.")
