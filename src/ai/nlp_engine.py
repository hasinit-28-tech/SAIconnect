
"""
SRIGITAM AI - Multilingual Deep Learning NLP Engine

Uses a multilingual Sentence Transformer to identify
student admission enquiry intents through semantic similarity.
"""

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sentence_transformers import util

logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Confidence threshold: uncertain messages are handled by fallback.
CONFIDENCE_THRESHOLD = 0.40

INTENT_EXAMPLES = {
    "greeting": [
        "Hi",
        "Hello",
        "Good morning",
        "నమస్కారం",
        "హలో",
        "Namaskaram",
    ],

    "course_list": [
        "What courses are available?",
        "Show me the list of courses",
        "Which courses does the college offer?",
        "మీ కాలేజీలో ఏ కోర్సులు ఉన్నాయి?",
        "Courses enti?",
        "Course list cheppandi",
    ],

    "fees": [
        "What is the course fee?",
        "How much are the fees?",
        "MLT fee entha?",
        "ఫీజు ఎంత?",
        "Course fees cheppandi",
        "How much does admission cost?",
    ],

    "eligibility": [
        "What is the eligibility?",
        "What qualification is required?",
        "Who can apply for this course?",
        "ఈ కోర్సుకు అర్హత ఏమిటి?",
        "Eligibility enti?",
    ],

    "duration": [
        "How long is the course?",
        "What is the course duration?",
        "How many years does it take?",
        "కోర్సు ఎన్ని సంవత్సరాలు?",
        "Course duration entha?",
    ],

    "admission": [
        "How can I get admission?",
        "I want to join this college",
        "How do I apply?",
        "అడ్మిషన్ ఎలా తీసుకోవాలి?",
        "College lo join avvali",
    ],

    "contact": [
        "How can I contact the college?",
        "Give me the college phone number",
        "Where is the college located?",
        "కాలేజీని ఎలా సంప్రదించాలి?",
    ],
}


@lru_cache(maxsize=1)
def load_model():
    """Load and cache the multilingual transformer model."""

    logger.info("Loading multilingual NLP model: %s", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME)

    logger.info("Multilingual NLP model loaded successfully.")

    return model


@lru_cache(maxsize=1)
def get_intent_embeddings():
    """Encode all example sentences once."""

    model = load_model()

    intent_names = []
    example_sentences = []

    for intent, examples in INTENT_EXAMPLES.items():
        for example in examples:
            intent_names.append(intent)
            example_sentences.append(example)

    embeddings = model.encode(
        example_sentences,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    return intent_names, embeddings


def predict_intent(message):
    """
    Predict the intent of a student message.

    Returns:
        intent, confidence
    """

    if not isinstance(message, str) or not message.strip():
        return "unknown", 0.0

    try:
        model = load_model()

        intent_names, intent_embeddings = get_intent_embeddings()

        message_embedding = model.encode(
            message,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        similarities = util.cos_sim(
            message_embedding,
            intent_embeddings,
        )[0]

        best_index = int(similarities.argmax().item())

        confidence = float(similarities[best_index].item())

        predicted_intent = intent_names[best_index]

        if confidence < CONFIDENCE_THRESHOLD:
            return "unknown", confidence

        logger.info(
            "Predicted intent: %s | Confidence: %.3f",
            predicted_intent,
            confidence,
        )

        return predicted_intent, confidence

    except Exception:
        logger.exception("NLP intent prediction failed.")
        return "unknown", 0.0
