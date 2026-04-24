import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skill_dictionary import SKILL_WEIGHTS


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

def match_skills_semantic(resume_skills, job_skills, threshold=0.6):

    matched = []
    missing = []
    explanations = []

    total_weight = 0
    matched_weight = 0

    if len(resume_skills) == 0:
        return [], job_skills, 0, ["No skills found in resume"]

    resume_embeddings = model.encode(resume_skills)
    job_embeddings = model.encode(job_skills)

    for i, job_vec in enumerate(job_embeddings):

        similarities = cosine_similarity([job_vec], resume_embeddings)[0]
        max_sim = max(similarities)  

        skill = job_skills[i]
        weight = SKILL_WEIGHTS.get(skill.lower(), 1)

        total_weight += weight

        if max_sim >= threshold:
            matched.append(skill)
            matched_weight += weight

            explanations.append(
                f"{skill} matched strongly (similarity: {max_sim:.2f}, weight: {weight})"
            )
        else:
            missing.append(skill)

            explanations.append(
                f"{skill} missing (weight: {weight})"
            )

    score = (matched_weight / total_weight) * 100 if total_weight else 0

    return matched, missing, score, explanations, matched_weight, total_weight