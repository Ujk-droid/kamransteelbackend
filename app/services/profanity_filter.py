import re

# Basic first-line-of-defense blocklist. Not exhaustive, not AI-based -
# just enough to catch obvious bad-language submissions before they reach
# the admin queue. Extend this set as needed.
BLOCKED_WORDS = {
    "fuck",
    "shit",
    "bitch",
    "asshole",
    "bastard",
    "cunt",
    "dick",
    "piss",
    "slut",
    "whore",
}


def _words(text: str) -> set:
    return set(re.sub(r"[^a-z0-9\s]", "", text.lower()).split())


def contains_profanity(text: str) -> bool:
    return bool(_words(text) & BLOCKED_WORDS)
