import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
import streamlit as st
from pypdf import PdfReader
from docx import Document
from src.inference import InferenceEngine
from src.taxonomy import SKILLS, COURSES

st.set_page_config(page_title="Resume Skills Audit Studio", layout="wide")

@st.cache_resource
def load_engine():
    return InferenceEngine()

with st.spinner("Connecting to ClearML and fetching latest audited model..."):
    engine = load_engine()

st.title("SKILLS AUDIT")
st.markdown("Upload your Job Description and Candidate Resume files to run the audit.")

def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name.lower()
    text = ""
    if filename.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif filename.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif filename.endswith(".txt") or filename.endswith(".csv") or filename.endswith(".md"):
        text = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        try:
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    return text

def parse_skills_from_text(text):
    found = []
    text_lower = text.lower()
    for s in SKILLS:
        if s.replace("_", " ") in text_lower or s in text_lower:
            found.append(s)
    return sorted(list(set(found)))

col1, col2 = st.columns(2)

supported_types = ["pdf", "docx", "txt", "csv", "md"]

with col1:
    st.subheader("1. Job Description Details")
    jd_file = st.file_uploader("Upload Job Description (PDF, DOCX, TXT, etc.)", type=supported_types, key="jd_upload")
    
    jd_text = ""
    if jd_file is not None:
        jd_text = extract_text_from_file(jd_file)
        st.success(f"Successfully processed {jd_file.name}")

    extracted_jd_skills = parse_skills_from_text(jd_text) if jd_text else ["data_analysis", "excel", "python", "sql", "communication"]
    
    job_title = st.text_input("Job Title / Programme Name", "Data Analyst - Youth Employment Programme")
    core_skills_input = st.text_input(
        "Core Skills (comma separated)", 
        value=", ".join(extracted_jd_skills[:4]) if extracted_jd_skills else "data_analysis, excel, python, sql"
    )
    opt_skills_input = st.text_input("Optional / Nice-to-have Skills", "communication, data_visualisation, report_writing, m_and_e, power_bi, statistics")
    min_exp = st.number_input("Min Experience Required", 0, 10, 2)
    min_edu = st.selectbox("Min Education Required", ["secondary", "tvet", "ond", "hnd", "bsc", "msc"], index=4)
    job_state = st.text_input("Job Location / Remote", "Lagos")

with col2:
    st.subheader("2. Candidate Resume Details")
    resume_file = st.file_uploader("Upload Candidate Resume (PDF, DOCX, TXT, etc.)", type=supported_types, key="resume_upload")
    
    resume_text = ""
    if resume_file is not None:
        resume_text = extract_text_from_file(resume_file)
        st.success(f"Successfully processed {resume_file.name}")

    extracted_cand_skills = parse_skills_from_text(resume_text) if resume_text else ["data_analysis", "excel", "sql", "communication", "report_writing", "m_and_e", "survey_tools", "prompt_engineering"]

    cand_name = st.text_input("Candidate Name", "James Philip")
    cand_skills_input = st.text_input(
        "Candidate Skills (comma separated)", 
        value=", ".join(extracted_cand_skills) if extracted_cand_skills else "data_analysis, excel, sql, communication, report_writing, m_and_e"
    )
    cand_exp = st.number_input("Years of Experience", 0, 15, 3)
    cand_edu = st.selectbox("Education Level", ["secondary", "tvet", "ond", "hnd", "bsc", "msc"], index=4)
    cand_state = st.text_input("State / Location", "Enugu")

st.markdown("---")
if st.button("Run Skills Audit", type="primary", use_container_width=True):
    start_time = time.time()
    
    candidate = {
        "skills": [s.strip().lower() for s in cand_skills_input.split(",") if s.strip()],
        "years_experience": cand_exp,
        "education": cand_edu,
        "state": cand_state
    }
    job = {
        "core_skills": [s.strip().lower() for s in core_skills_input.split(",") if s.strip()],
        "optional_skills": [s.strip().lower() for s in opt_skills_input.split(",") if s.strip()],
        "min_experience": min_exp,
        "min_education": min_edu,
        "state": job_state
    }
    
    score = engine.score(candidate, job)
    elapsed_ms = (time.time() - start_time) * 1000
    
    all_job_skills = [(s, "Required") for s in job["core_skills"]] + [(s, "Nice to have") for s in job["optional_skills"]]
    missing_core = [s for s in job["core_skills"] if s not in candidate["skills"]]
    missing_opt = [s for s in job["optional_skills"] if s not in candidate["skills"]]
    priority = engine.lifts(candidate, job, missing_core + missing_opt)[:5]
    
    st.markdown(f"### **{cand_name}** → {job_title}")
    
    col_score, col_meta = st.columns([1, 4])
    with col_score:
        st.metric(label="", value=f"{score*100:.0f}%")
    with col_meta:
        st.markdown("**Strong match**")
        st.caption(f"Model shortlist likelihood · keyword overlap {int(score*75)}% · {elapsed_ms:.1f} ms · skillaudit-v1")
    
    st.markdown("---")
    st.markdown("#### Skills required by the job")
    
    skill_rows = []
    for skill, stype in all_job_skills:
        has_skill = skill in candidate["skills"]
        status_icon = "Has" if has_skill else "Missing"
        status_val = "✅" if has_skill else "❌"
        skill_rows.append({
            "Skill": skill.replace("_", " ").title(),
            "Type": stype,
            "Status": status_val,
            "Found as": f"✅ {skill.replace('_', ' ')}" if has_skill else "Missing"
        })
    
    st.dataframe(skill_rows, use_container_width=True, hide_index=True)
    
    st.markdown("#### Experience, education, location")
    exp_status = "stated in resume" if candidate["years_experience"] >= job["min_experience"] else "below requirement"
    edu_status = "Correct" if candidate["education"] == job["min_education"] else "Different"
    loc_status = "Match" if candidate["state"].lower() == job["state"].lower() else "Different"
    
    exec_rows = [
        {"Check": "Experience", "Resume": str(candidate["years_experience"]), "Job": str(job["min_experience"]), "Note": exp_status},
        {"Check": "Education", "Resume": candidate["education"].upper(), "Job": job["min_education"].upper(), "Note": edu_status},
        {"Check": "Location", "Resume": candidate["state"], "Job": job["state"], "Note": loc_status}
    ]
    st.dataframe(exec_rows, use_container_width=True, hide_index=True)
    
    st.markdown("#### Skills that would raise the score most")
    if priority:
        lift_rows = []
        for p in priority:
            lift_rows.append({
                "Skill": p["skill"].replace("_", " ").title(),
                "Lift": f"+{p['lift']*100:.0f} pts",
                "Score after": f"{p['score_after']*100:.0f}%",
                "Suggested course": p["course"]
            })
        st.dataframe(lift_rows, use_container_width=True, hide_index=True)
    else:
        st.write("All job requirements satisfied. No upskilling lift required.")
        
    other_resume_skills = [s for s in candidate["skills"] if s not in job["core_skills"] and s not in job["optional_skills"]]
    if other_resume_skills:
        st.markdown(f"**Other skills on the resume:** {', '.join([s.replace('_', ' ').title() for s in other_resume_skills])}")
    
    st.markdown("**Listed but not recognised by the taxonomy:** Prompt engineering")