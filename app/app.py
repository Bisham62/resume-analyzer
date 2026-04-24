import streamlit as st
import sys
import os
import tempfile

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from utils.skill_dictionary import SKILL_WEIGHTS
from nlp.matcher import match_skills_semantic
from nlp.skill_extractor import extract_skills_nlp


from parser.resume_parser import (
    extract_text_from_pdf,
    extract_name,
    extract_job_skills,
)

def get_priority_recommendations(missing_skills):
    return sorted(
        missing_skills,
        key=lambda x: SKILL_WEIGHTS.get(x.lower(), 1),
        reverse=True
    )


st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")
st.caption("Analyze your resume against job descriptions using AI-powered matching")

with st.expander("How this helps job seekers"):
    st.markdown("""
    - Understand how well your resume matches a job  
    - Identify missing high-impact skills  
    - Focus on what actually matters to recruiters  
    """)

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
job_description = st.text_area("Paste Job Description")

if st.button("Analyze"):
    if uploaded_file and job_description:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name


        try:
            text = extract_text_from_pdf(temp_path)
        except Exception:
            st.error("Failed to read PDF. Please upload a valid file.")
            st.stop()

        name = extract_name(text)

        cleaned = extract_skills_nlp(text)

        job_skills = extract_job_skills(job_description)
        matched, missing, score, explanations, matched_weight, total_weight = match_skills_semantic(cleaned, job_skills)

        st.subheader("Results")

        st.write("Name:", name)
        st.write(f"Match Score: {score:.2f}%")
        st.caption(f"Weighted Score: {matched_weight} / {total_weight}")
        st.progress(score / 100)

        st.write(f"You matched {len(matched)} out of {len(job_skills)} required skills.")

        st.subheader("Matched Skills")
        for skill in matched:
            st.success(skill.capitalize())

        st.subheader("Missing Skills")
        for skill in missing:
            st.error(skill.capitalize())


        st.subheader("Skill Distribution")

        st.bar_chart({
            "Matched": matched_weight,
            "Missing": total_weight - matched_weight
        })

        if missing:
            priority_skills = get_priority_recommendations(missing)

            st.subheader("Priority Skills to Learn")
            for skill in priority_skills:
                weight = SKILL_WEIGHTS.get(skill.lower(), 1)
                
                if weight == 3:
                    level = "High Priority"
                elif weight == 2:
                    level = "Medium Priority"
                else:
                    level = "Low Priority"

                st.write(f"- {skill.capitalize()} ({level})")

        if missing:
            st.subheader("Learning Roadmap")
            for skill in priority_skills:
                st.write(f"Learn {skill.capitalize()} to improve your match score")      
        
        st.subheader("Why this score?")
        for exp in explanations:
            st.caption(f"- {exp}")


        if score >= 80:
            st.success("Excellent match! You are highly aligned with this role.")
        elif score >= 60:
            st.warning("Good match. Strengthen key missing skills.")
        elif score >= 40:
            st.warning("Moderate match. Focus on important skills.")
        else:
            st.error("Low match. Significant skill gaps detected.")
       
    else:
        st.warning("Please upload a resume and enter a job description.")