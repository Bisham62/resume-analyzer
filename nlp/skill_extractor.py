import spacy
from utils.skill_dictionary import SKILL_LIST

nlp = spacy.load("en_core_web_sm")

SKILL_ALIASES = {
    "reactjs": "react",
    "nodejs": "nodejs",
    "js": "javascript"
}

def normalize_text(text):
    return text.lower()    

def extract_skills_nlp(text):
    text = normalize_text(text)
    doc = nlp(text)

    found_skills = set()
    tokens = [token.text.lower() for token in doc]
    text_joined = " ".join(tokens)

    for skill in SKILL_LIST:
        skill_tokens = skill.lower().split()

        
        if " ".join(skill_tokens) in text_joined:
            found_skills.add(skill)

    normalized_skills = set()

    for skill in found_skills:
        key = skill.lower()
        normalized_skills.add(SKILL_ALIASES.get(key, skill))

    return list(normalized_skills)  

