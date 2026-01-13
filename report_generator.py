import random

# ================= IMPORT STATEMENTS =================
import statements_igcse_0510_esl as esl
import statements_igcse_0620_chemistry as chem

# ================= SUBJECT MAP =================
SUBJECTS = {
    "IGCSE ESL 0510": {
        "opening": esl.opening_phrases,
        "skills": [
            esl.listening_statements,
            esl.speaking_statements,
            esl.reading_statements,
            esl.writing_statements
        ],
        "closing": esl.closing_statements
    },
    "IGCSE Chemistry 0620": {
        "opening": chem.opening_phrases,
        "skills": [
            chem.knowledge_statements,
            chem.practical_statements,
            chem.analysis_statements,
            chem.exam_statements
        ],
        "closing": chem.closing_statements
    }
}

# ================= GENERATOR FUNCTION =================
def generate_report(subject: str) -> str:
    if subject not in SUBJECTS:
        return "ERROR: Subject not recognised."

    data = SUBJECTS[subject]

    opening = random.choice(data["opening"])
    skills = " ".join(random.choice(skill) for skill in data["skills"])
    closing = random.choice(data["closing"])

    return f"{opening} {skills} {closing}"

# ================= TEST =================
if __name__ == "__main__":
    print("----- ESL SAMPLE -----")
    print(generate_report("IGCSE ESL 0510"))
    print()
    print("----- CHEMISTRY SAMPLE -----")
    print(generate_report("IGCSE Chemistry 0620"))
