
"""
SRIGITAM AI - Multilingual Admission Conversation Engine

Combines:
1. Multilingual Sentence Transformer NLP
2. Rule-based course detection
3. Verified college knowledge base
4. English, Telugu and Romanized Telugu support

Unknown college information is never invented.
"""

import logging

from src.ai.knowledge_base import (
    COLLEGE,
    COURSES,
    get_course_list,
)
from src.ai.nlp_engine import predict_intent

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. LANGUAGE DETECTION
# --------------------------------------------------

def detect_language(message):
    """Detect Telugu, English or Romanized Telugu."""

    text = message.lower()

    telugu_chars = any(
        "\u0C00" <= char <= "\u0C7F"
        for char in message
    )

    if telugu_chars:
        return "telugu"

    telugu_words = [
        "namaskaram",
        "cheppandi",
        "kavali",
        "undi",
        "chesukovali",
        "entha",
        "enti",
        "cheppu",
        "avvali",
        "ledu",
    ]

    if any(word in text for word in telugu_words):
        return "mixed"

    return "english"


# --------------------------------------------------
# 2. COURSE DETECTION
# --------------------------------------------------

def detect_course(message):
    """Identify the course mentioned by the student."""

    text = message.lower()

    course_keywords = {
        "MLT": [
            "mlt",
            "medical laboratory",
            "medical lab",
            "lab technician",
            "laboratory technology",
        ],
        "MPHW": [
            "mphw",
            "health worker",
            "multi purpose health worker",
            "multipurpose health worker",
        ],
        "CSE": [
            "cse",
            "computer science",
            "computer engineering",
        ],
        "AT": [
            "accounting and taxation",
            "accounting",
            "taxation",
            "accounts",
        ],
    }

    for course_code, keywords in course_keywords.items():
        if any(keyword in text for keyword in keywords):
            return course_code

    return None


# --------------------------------------------------
# 3. GREETING DETECTION
# --------------------------------------------------

def is_greeting(message):
    """Check common greeting messages."""

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste",
        "namaskaram",
        "హాయ్",
        "హలో",
        "నమస్కారం",
    ]

    return message.lower().strip() in greetings


def greeting_reply(language):
    """Generate a greeting in the detected language."""

    if language == "telugu":
        return (
            f"నమస్కారం! {COLLEGE['name']} కు స్వాగతం! 😊\n\n"
            "నేను SRIGITAM AI, మీ అడ్మిషన్ అసిస్టెంట్.\n\n"
            "మీకు ఏ విధంగా సహాయం చేయగలను?\n\n"
            "1. అందుబాటులో ఉన్న కోర్సులు\n"
            "2. కోర్సు వివరాలు\n"
            "3. అడ్మిషన్ వివరాలు"
        )

    return (
        f"Hello! Welcome to {COLLEGE['name']}! 😊\n\n"
        "I am SRIGITAM AI, your admission assistant.\n\n"
        "How can I help you?\n\n"
        "1. View available courses\n"
        "2. Course details\n"
        "3. Admission enquiry"
    )


# --------------------------------------------------
# 4. COURSE LIST
# --------------------------------------------------

def course_list_reply(language):
    """Return the courses in the knowledge base."""

    courses = "\n".join(
        f"• {course}"
        for course in get_course_list()
    )

    if language == "telugu":
        return (
            "మా కళాశాల నాలెడ్జ్ బేస్‌లో ఉన్న కోర్సులు:\n\n"
            f"{courses}\n\n"
            "మీకు ఏ కోర్సు గురించి వివరాలు కావాలి?"
        )

    return (
        "These are the courses listed in our college "
        "knowledge base:\n\n"
        f"{courses}\n\n"
        "Which course would you like to know about?"
    )


# --------------------------------------------------
# 5. RULE-BASED ENQUIRY DETECTION
# --------------------------------------------------

def detect_course_question(text):
    """Detect a specific course enquiry using keywords."""

    text = text.lower()

    fee_keywords = [
        "fee", "fees", "cost", "tuition",
        "fee entha", "fees entha",
        "ఫీజు", "ఫీజులు",
    ]

    eligibility_keywords = [
        "eligibility", "qualification",
        "qualification required", "eligible",
        "ఏ అర్హత", "అర్హత",
    ]

    duration_keywords = [
        "duration", "how many years",
        "course length", "course period",
        "ఎన్ని సంవత్సరాలు", "ఎంత కాలం",
    ]

    admission_keywords = [
        "admission", "join", "apply",
        "admission process", "how to join",
        "చేరాలి", "అడ్మిషన్",
    ]

    if any(word in text for word in fee_keywords):
        return "fees"

    if any(word in text for word in eligibility_keywords):
        return "eligibility"

    if any(word in text for word in duration_keywords):
        return "duration"

    if any(word in text for word in admission_keywords):
        return "admission"

    return None


# --------------------------------------------------
# 6. COURSE-SPECIFIC RESPONSES
# --------------------------------------------------

def course_enquiry_reply(course_code, question_type):
    """Answer course questions using verified information."""

    course = COURSES[course_code]
    course_name = course["name"]
    verified_details = course.get("verified_details", {})

    if question_type == "fees":
        fee = verified_details.get("fees")

        if fee:
            return f"The verified fee for {course_name} is {fee}."

        return (
            f"Course: {course_name}\n\n"
            "The verified fee information has not yet been "
            "added to our college database.\n\n"
            "Our admission team can confirm the exact fee."
        )

    if question_type == "eligibility":
        eligibility = verified_details.get("eligibility")

        if eligibility:
            return (
                f"Eligibility for {course_name}:\n"
                f"{eligibility}"
            )

        return (
            f"Course: {course_name}\n\n"
            "The eligibility criteria have not yet been "
            "verified in our college database.\n\n"
            "Please contact our admission team for confirmation."
        )

    if question_type == "duration":
        duration = verified_details.get("duration")

        if duration:
            return (
                f"The verified duration of {course_name} "
                f"is {duration}."
            )

        return (
            f"Course: {course_name}\n\n"
            "The verified course duration has not yet "
            "been added to our college database."
        )

    if question_type == "admission":
        return (
            f"Thank you for your interest in {course_name}!\n\n"
            "I can help you with your admission enquiry.\n\n"
            "May I know your name?"
        )

    return (
        f"Course: {course_name}\n\n"
        "What would you like to know?\n\n"
        "1. Fees\n"
        "2. Eligibility\n"
        "3. Course duration\n"
        "4. Admission process"
    )


# --------------------------------------------------
# 7. GENERAL ENQUIRY RESPONSES
# --------------------------------------------------

def ask_course_reply(question_type):
    """Ask which course the student is interested in."""

    if question_type == "fees":
        opening = "I'd be happy to help with the fee details!"

    elif question_type == "eligibility":
        opening = "I can help you with eligibility details."

    elif question_type == "duration":
        opening = "I can help you with course duration."

    else:
        opening = "Thank you for your admission enquiry!"

    return (
        f"{opening}\n\n"
        "Which course are you interested in?\n\n"
        "1. MLT\n"
        "2. MPHW (Female)\n"
        "3. CSE\n"
        "4. Accounting and Taxation"
    )


# --------------------------------------------------
# 8. MAIN CONVERSATION ENGINE
# --------------------------------------------------

def generate_reply(message):
    """Generate an admission response using NLP and rules."""

    if not isinstance(message, str) or not message.strip():
        return "Please send a message so I can help you."

    message = message.strip()
    text = message.lower()
    language = detect_language(message)

    logger.info(
        "Processing message. Detected language: %s",
        language,
    )

    # Run the multilingual NLP model.
    predicted_intent, confidence = predict_intent(message)

    logger.info(
        "NLP intent: %s | Similarity: %.3f",
        predicted_intent,
        confidence,
    )

    # GREETING
    if is_greeting(message) or predicted_intent == "greeting":
        return greeting_reply(language)

    # COURSE LIST
    course_list_keywords = [
        "courses",
        "course list",
        "what courses",
        "available courses",
        "courses enti",
        "ఏ కోర్సులు",
        "కోర్సులు",
    ]

    if (
        predicted_intent == "course_list"
        or any(word in text for word in course_list_keywords)
    ):
        return course_list_reply(language)

    # Identify course and enquiry type.
    course_code = detect_course(message)
    question_type = detect_course_question(text)

    # Use NLP intent when keyword detection does not identify
    # the enquiry type.
    intent_mapping = {
        "fees": "fees",
        "eligibility": "eligibility",
        "duration": "duration",
        "admission": "admission",
    }

    if question_type is None:
        question_type = intent_mapping.get(predicted_intent)

    # COURSE-SPECIFIC ENQUIRY
    if course_code:
        return course_enquiry_reply(
            course_code,
            question_type,
        )

    # GENERAL ENQUIRY WITHOUT COURSE
    if question_type in [
        "fees",
        "eligibility",
        "duration",
        "admission",
    ]:
        return ask_course_reply(question_type)

    # CONTACT ENQUIRY
    if predicted_intent == "contact":
        return (
            "I can help you with college contact information.\n\n"
            "The verified phone number and contact details "
            "have not yet been added to our database.\n\n"
            "Please contact the college admission team "
            "for assistance."
        )

    # FALLBACK
    return (
        f"Thank you for contacting {COLLEGE['name']}! 😊\n\n"
        "I am SRIGITAM AI, your admission assistant.\n\n"
        "I can help you with:\n\n"
        "• Available courses\n"
        "• Course information\n"
        "• Fees enquiries\n"
        "• Eligibility enquiries\n"
        "• Course duration\n"
        "• Admission process\n\n"
        "Please tell me what you would like to know."
    )
