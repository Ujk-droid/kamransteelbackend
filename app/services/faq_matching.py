import re
from difflib import SequenceMatcher
from typing import List

from app.models.faq import FAQ
from app.schemas.faq import AskResponse

MATCH_THRESHOLD = 0.4
FALLBACK_ANSWER = (
    "Sorry, I couldn't find an answer to that. Please reach out to us on WhatsApp."
)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()


def _keyword_overlap(a: str, b: str) -> float:
    words_a = set(_normalize(a).split())
    words_b = set(_normalize(b).split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / min(len(words_a), len(words_b))


def _score(message: str, question: str) -> float:
    sequence_score = SequenceMatcher(None, _normalize(message), _normalize(question)).ratio()
    keyword_score = _keyword_overlap(message, question)
    return max(sequence_score, keyword_score)


def find_best_match(message: str, faqs: List[FAQ]) -> AskResponse:
    best_faq = None
    best_score = 0.0

    for faq in faqs:
        score = _score(message, faq.question)
        if score > best_score:
            best_score = score
            best_faq = faq

    if best_faq is not None and best_score >= MATCH_THRESHOLD:
        return AskResponse(matched=True, answer=best_faq.answer, faq_id=best_faq.id)

    return AskResponse(matched=False, answer=FALLBACK_ANSWER, faq_id=None)
