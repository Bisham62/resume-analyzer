from utils.skill_dictionary import SKILL_LIST
from PyPDF2 import PdfReader
import re


# -----------------------------
# Normalize text (IMPORTANT)
# -----------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\. ]", "", text)  # keep spaces
    return text.strip()


# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Extract name (first line)
# -----------------------------
def extract_name(text):
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if line:
            return line

    return "Name not found"


# -----------------------------
# Extract skills section
# -----------------------------
def extract_skills(text):
    lines = text.split("\n")
    skills = []
    capture = False

    for line in lines:
        line = line.strip()

        if "SKILLS" in line.upper():
            capture = True
            continue

        if capture and line.isupper() and len(line) < 30:
            break

        if capture:
            skills.append(line)

    return skills


# -----------------------------
# Clean extracted skills
# -----------------------------
def clean_skills(skill_lines):
    skills = []

    for line in skill_lines:
        line = re.sub(r"[^\w\s,+#\.]", "", line)

        parts = line.split(",")

        for part in parts:
            skill = part.strip()

            if not skill:
                continue

            if skill.lower() in ["in", "and"]:
                continue

            if len(skill.split()) > 3:
                continue

            skills.append(skill)

    return skills


# -----------------------------
# Extract job skills
# -----------------------------
def extract_job_skills(job_description):
    job_description = normalize_text(job_description)

    found_skills = set()

    for skill in SKILL_LIST:
        skill_tokens = skill.lower().split()

        if " ".join(skill_tokens) in job_description:
            found_skills.add(skill)

    return list(found_skills)


# -----------------------------
# Match skills (SMART LOGIC)
# -----------------------------
def match_skills(resume_skills, job_skills):
    matched = []
    missing = []

    normalized_resume = [normalize_text(r) for r in resume_skills]

    for skill in job_skills:
        norm_skill = normalize_text(skill)

        if any(
            norm_skill in r
            or r in norm_skill
            or norm_skill.replace(" ", "") in r.replace(" ", "")
            for r in normalized_resume
        ):
            matched.append(skill)
        else:
            missing.append(skill)

    score = (len(matched) / len(job_skills)) * 100 if job_skills else 0

    return matched, missing, score


# -----------------------------
# MAIN (for terminal testing)
# -----------------------------
if __name__ == "__main__":
    file_path = "sample_resume.pdf"

    extracted_text = extract_text_from_pdf(file_path)

    print("\n--- EXTRACTED TEXT ---\n")
    print(extracted_text)

    name = extract_name(extracted_text)
    print("\n--- EXTRACTED NAME ---\n")
    print(name)

    skills = extract_skills(extracted_text)
    print("\n--- EXTRACTED SKILLS ---\n")
    for skill in skills:
        print(skill)

    cleaned_skills = clean_skills(skills)
    print("\n--- CLEANED SKILLS ---\n")
    for skill in cleaned_skills:
        print(skill)

    job_description = input("\nEnter job description:\n")

    job_skills = extract_job_skills(job_description)

    matched, missing, score = match_skills(cleaned_skills, job_skills)

    print("\n=== MATCH RESULTS ===")

    print("\nMatched Skills:")
    for skill in matched:
        print(f"- {skill.capitalize()}")

    print("\nMissing Skills:")
    for skill in missing:
        print(f"- {skill.capitalize()}")

    print(f"\nMatch Score: {score:.2f}%")

    if score >= 75:
        print("\nStrong match! You are well aligned with this role.")
    elif score >= 50:
        print("\nDecent match. Consider improving missing skills.")
    else:
        print("\nLow match. You need to build more relevant skills.")