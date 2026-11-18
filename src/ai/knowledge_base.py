
"""
SAIConnect - Sai University Knowledge Base
University facts are based on information supplied
from Sai University's official website.
"""

UNIVERSITY = {
    "name": "Sai University",
    "short_name": "SAIU",
    "address": (
        "One Hub Road, Old Mahabalipuram Road, "
        "Paiyanur, Tamil Nadu, Chennai - 603104"
    ),
    "email": "admissions@saiuniversity.edu.in",
    "general_phone": "044 7143 7200",
    "admissions_phones": [
        "+91 91500 75661",
        "+91 91500 75662",
        "+91 91500 75663"
    ],
    "website": "https://www.saiuniversity.edu.in/",
    "application_url": "https://apply.saiuniversity.edu.in/"
}

SCHOOLS = [
    "School of Law",
    "School of Arts and Sciences",
    "School of Computing and Data Science",
    "School of Artificial Intelligence",
    "School of Business",
    "School of Media",
    "School of Technology",
    "School of Allied Health Sciences"
]

PROGRAMS = {
    "School of Arts and Sciences": {
        "B.Sc. (Hons.) Neuroscience": {
            "major": "Cognitive Neuroscience",
            "key_courses": [
                "Developmental Neuroscience",
                "Cognitive and Behavioral Neuroscience",
                "Neurogenetics",
                "Neuropathology and Therapeutics",
                "Neurophysiology",
                "Neurochemistry"
            ]
        },

        "B.Sc. (Hons.) Biological Sciences": {
            "major": "Biological Sciences",
            "specialisations": [
                "Microbiology",
                "Medical Sciences",
                "Molecular Biology",
                "Bioinformatics",
                "Genetics",
                "Computational Biology with AI",
                "Immunology",
                "Environmental Biotechnology",
                "Biochemistry"
            ]
        },

        "B.Sc. (Hons.) Psychology": {
            "major": "Psychology",
            "specialisations": [
                "Introduction to Psychology",
                "Social and Political Psychology",
                "Social Psychology",
                "Sports Psychology",
                "Counseling Psychology",
                "Consumer Psychology",
                "Psychopathology",
                "Clinical Psychology",
                "Research Methods",
                "Organizational Behavior",
                "Developmental Psychology"
            ]
        },

        "B.A. (Hons.) Economics": {
            "major": "Economics",
            "key_courses": [
                "Foundations of Economics",
                "Development Economics",
                "Applied Mathematics for Economics",
                "Financial Economics and Data Analytics",
                "Principles of Economics",
                "Behavioural Economics and Decision Sciences",
                "Modern Indian Economy",
                "Applied Probability for Economics",
                "Microeconomics II",
                "Macroeconomics II",
                "Politics, Economics, and the Environment"
            ]
        },

        "B.A. (Hons.) Politics, Philosophy, and Economics (PPE)": {
            "major": "Politics, Philosophy, and Economics",
            "key_courses": [
                "Foundations of Economics",
                "Principles of Economics",
                "Applied Probability for Economics",
                "Modern Indian Economy",
                "Introduction to Philosophy",
                "Philosophy of Science",
                "Metaphysics",
                "Ethics",
                "Modern Political Thought",
                "Indian Politics",
                "Politics, Economics, and the Environment"
            ]
        }
    }
}

UNIVERSITY_FACTS = {
    "schools_count": 8,
    "programs_count": 30,
    "program_levels": [
        "Undergraduate",
        "Postgraduate",
        "Doctoral"
    ],
    "ai_integration": "AI integration across disciplines"
}


def get_university_details():
    return UNIVERSITY


def get_college_details():
    return UNIVERSITY


def get_school_list():
    return SCHOOLS


def get_course_list():
    courses = []

    for school, programs in PROGRAMS.items():
        for program in programs:
            courses.append(f"{program} - {school}")

    return courses


def get_course_details(course_name):
    search = course_name.lower()

    for school, programs in PROGRAMS.items():
        for name, details in programs.items():
            if search in name.lower():
                return {
                    "school": school,
                    "program": name,
                    **details
                }

    return None


def get_contact_details():
    return {
        "email": UNIVERSITY["email"],
        "general_phone": UNIVERSITY["general_phone"],
        "admissions_phones": UNIVERSITY["admissions_phones"],
        "address": UNIVERSITY["address"],
        "website": UNIVERSITY["website"]
    }
