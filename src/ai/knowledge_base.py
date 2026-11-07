
"""
SRIGITAM AI - College Knowledge Base

Only verified college information should be added here.
Unknown information must not be invented by the AI.
"""

COLLEGE = {
    "name": "Srigitam Vocational Junior College",
    "location": "Rajahmundry",
}

COURSES = {
    "MLT": {
        "name": "Medical Laboratory Technology",
        "verified_details": {},
    },
    "MPHW": {
        "name": "Multi Purpose Health Worker (Female)",
        "verified_details": {},
    },
    "CSE": {
        "name": "Computer Science and Engineering",
        "verified_details": {},
    },
    "AT": {
        "name": "Accounting and Taxation",
        "verified_details": {},
    },
}

def get_course_list():
    """Return the currently offered courses."""
    return [
        f"{code} - {details['name']}"
        for code, details in COURSES.items()
    ]


def get_course_details(course_code):
    """Return verified information for a course."""
    return COURSES.get(course_code.upper())


def get_college_details():
    """Return basic college information."""
    return COLLEGE
