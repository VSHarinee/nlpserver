# import spacy
# import re
# import json
# import os
# from spellchecker import SpellChecker

# spell = SpellChecker()

# def correct_action_text(action_text):
#     if not action_text:
#         return action_text

#     corrected_words = []

#     for word in action_text.split():
#         if word.isalpha() and len(word) > 3:
#             corrected_word = spell.correction(word)
#             corrected_words.append(corrected_word if corrected_word else word)
#         else:
#             corrected_words.append(word)

#     return " ".join(corrected_words)

# # ---------------------------------------
# # Load NLP
# # ---------------------------------------
# nlp = spacy.load("en_core_web_sm")

# # ---------------------------------------
# # Constants
# # ---------------------------------------
# SELF_WORDS = {"me", "myself", "i"}
# PRONOUNS = {"her", "him", "she", "he", "his"}

# MEMORY_FILE = "adaptive_memory.json"

# # ---------------------------------------
# # Load / Save Memory
# # ---------------------------------------
# def load_memory():
#     if os.path.exists(MEMORY_FILE):
#         with open(MEMORY_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_memory(memory):
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(memory, f, indent=4)

# ADAPTIVE_MEMORY = load_memory()

# # ---------------------------------------
# # Reminder Engine
# # ---------------------------------------
# def reminder_engine(text, friend_list):

#     text_key = text.strip().lower()

#     # Adaptive Memory Override
#     if text_key in ADAPTIVE_MEMORY:
#         return ADAPTIVE_MEMORY[text_key]

#     doc = nlp(text)

#     action = None
#     location = None
#     person = None
#     confidence = 0.8

#     # Intent Detection
#     intent_detected = False
#     for token in doc:
#         if token.lemma_.lower() in ["remind", "notify", "tell", "alert", "set", "create", "add", "schedule", "make"]:
#             intent_detected = True
#             break

#     if not intent_detected:
#         return {"error": "Not a location-based reminder"}

#     # Action Extraction
#     for token in doc:
#         if token.dep_ in ("xcomp", "ccomp"):
#             action = " ".join([child.text for child in token.subtree])
#             break

#     if not action:
#         match = re.search(r'to (.*?)( at | in | near | when |$)', text)
#         if match:
#             action = match.group(1).strip()

#     if action:
#         corrected_action = correct_action_text(action)
#     else:
#         corrected_action = None

#     action = corrected_action

#     if not action:
#         confidence -= 0.3

#     # Location Extraction
#     for ent in doc.ents:
#         if ent.label_ in ("GPE", "LOC", "FAC", "ORG"):
#             location = ent.text
#             break

#     if not location:
#         for token in doc:
#             if token.dep_ == "pobj" and token.head.text.lower() in ["at", "in", "near", "to", "reach", "around"]:
#                 location = " ".join([child.text for child in token.subtree])
#                 break

#     if not location:
#         confidence -= 0.3

#     # Person Extraction
#     friend_set = {friend.lower(): friend for friend in friend_list}

#     candidate_names = []

#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             candidate_names.append(ent.text.strip())

#     temp_name = []
#     for token in doc:
#         if token.pos_ == "PROPN":
#             temp_name.append(token.text)
#         else:
#             if temp_name:
#                 candidate_names.append(" ".join(temp_name))
#                 temp_name = []
#     if temp_name:
#         candidate_names.append(" ".join(temp_name))

#     candidate_names = list(set(candidate_names))

#     matched_friend = None

#     for name in candidate_names:
#         if name.lower() in friend_set:
#             matched_friend = friend_set[name.lower()]
#             break

#     if not matched_friend:
#         for token in doc:
#             if token.text.lower() in SELF_WORDS:
#                 matched_friend = "self"
#                 break

#     if not matched_friend:
#         for token in doc:
#             if token.text.lower() in PRONOUNS:
#                 matched_friend = "self"
#                 break

#     if not matched_friend:
#         matched_friend = "self"

#     person = matched_friend

#     confidence = max(0.0, min(1.0, confidence))

#     return {
#         "intent": "location_based_reminder",
#         "action": action,
#         "location": location,
#         "person": person,
#         "confidence": round(confidence, 2)
#     }

# # ---------------------------------------
# # Learning From User Correction
# # ---------------------------------------
# def learn_from_user_correction(original_text, corrected_output):
#     key = original_text.strip().lower()
#     ADAPTIVE_MEMORY[key] = corrected_output
#     save_memory(ADAPTIVE_MEMORY)

import spacy
import re
import json
import os
from spellchecker import SpellChecker

spell = SpellChecker()

# ---------------------------------------
# Spell Correction (unchanged)
# ---------------------------------------
def correct_action_text(action_text):
    if not action_text:
        return action_text
    corrected_words = []
    for word in action_text.split():
        if word.isalpha() and len(word) > 3:
            corrected_word = spell.correction(word)
            corrected_words.append(corrected_word if corrected_word else word)
        else:
            corrected_words.append(word)
    return " ".join(corrected_words)

# ---------------------------------------
# Load NLP
# ---------------------------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------
# Constants
# ---------------------------------------
SELF_WORDS = {"me", "myself", "i", "my"}
PRONOUNS    = {"her", "him", "she", "he", "his", "they", "them"}

INTENT_LEMMAS = {
    "remind", "notify", "tell", "alert",
    "set", "create", "add", "schedule", "make", "ping"
}

LOCATION_PREPS = {"at", "in", "near", "to", "around", "by", "outside", "inside", "from"}

MEMORY_FILE = "adaptive_memory.json"

# ---------------------------------------
# Load / Save Memory (unchanged)
# ---------------------------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

ADAPTIVE_MEMORY = load_memory()

# ---------------------------------------
# Helper: clean & normalise extracted text
# ---------------------------------------
def _clean(text: str) -> str:
    """Strip leading/trailing stopwords and whitespace from a phrase."""
    noise = {"the", "a", "an", "my", "your", "our", "their", "me", "him", "her"}
    words = text.strip().split()
    while words and words[0].lower() in noise:
        words.pop(0)
    while words and words[-1].lower() in noise:
        words.pop()
    return " ".join(words)

# ---------------------------------------
# Intent Detection (improved)
# ---------------------------------------
def _detect_intent(doc) -> bool:
    """Return True if the sentence looks like a reminder request."""
    for token in doc:
        if token.lemma_.lower() in INTENT_LEMMAS:
            return True
    # Fallback: imperative pattern — bare verb at start
    if doc and doc[0].pos_ == "VERB":
        return True
    return False

# ---------------------------------------
# Action Extraction (improved)
# ---------------------------------------
def _strip_leading_to(phrase: str) -> str:
    """Remove a leading 'to ' from an action phrase."""
    return re.sub(r'^to\s+', '', phrase, flags=re.IGNORECASE).strip()

def _extract_action(doc, text: str):
    """
    Prefer syntactic xcomp/ccomp subtree first,
    then LAST 'to <verb phrase>' regex (avoids grabbing 'to <person>'),
    then 'about <phrase>' hint.
    """
    # 1. Dependency parse — xcomp / ccomp
    for token in doc:
        if token.dep_ in ("xcomp", "ccomp"):
            phrase = " ".join(t.text for t in token.subtree)
            return _strip_leading_to(_clean(phrase))

    # 2. Regex: find ALL "to <verb phrase>" segments, take the LAST one.
    #    The capture stops at any location preposition — never includes it.
    matches = list(re.finditer(
        r'\bto\s+((?:(?!(?:at|in|near|by|around|outside|inside|from)\b)\S+\s*)+?)(?=\s+(?:at|in|near|by|around|outside|inside|from)\b|$)',
        text, re.IGNORECASE
    ))
    if matches:
        phrase = _clean(matches[-1].group(1))
        return _strip_leading_to(phrase)

    # 3. Regex: "about <action>"
    match = re.search(r'\babout\s+([\w\s]+?)(?:\s+(?:at|in|near|when|by|$))', text, re.IGNORECASE)
    if match:
        return _strip_leading_to(_clean(match.group(1)))

    return None

# ---------------------------------------
# Location Extraction (improved)
# ---------------------------------------
def _extract_location(doc, text: str):
    """
    1. Named entity (GPE / LOC / FAC / ORG)
    2. Prepositional object of a location preposition
    3. Regex 'at/in/near <place>'
    """
    # 1. NER
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "FAC", "ORG"):
            return _clean(ent.text)

    # 2. Dependency — pobj of location prep
    for token in doc:
        if token.dep_ == "pobj" and token.head.text.lower() in LOCATION_PREPS:
            phrase = " ".join(t.text for t in token.subtree)
            return _clean(phrase)

    # 3. Regex fallback
    preps_pattern = "|".join(LOCATION_PREPS)
    match = re.search(
        rf'\b(?:{preps_pattern})\s+(?:the\s+)?([\w\s]+?)(?:\s+(?:when|to|and|,)|$)',
        text, re.IGNORECASE
    )
    if match:
        candidate = _clean(match.group(1))
        # Avoid returning generic short words that aren't places
        if len(candidate.split()) >= 1 and len(candidate) > 2:
            return candidate

    return None

# ---------------------------------------
# Levenshtein distance (no extra deps)
# ---------------------------------------
def _levenshtein(a: str, b: str) -> int:
    """Pure-python edit distance between two strings."""
    a, b = a.lower(), b.lower()
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def _edit_distance_match_friend(candidate: str, friend_list: list, max_dist: int = 2) -> str | None:
    """
    Match `candidate` (a single word or full name) against every friend name
    using Levenshtein edit distance.  Matches only when the distance is
    ≤ max_dist AND ≤ 40 % of the longer string (avoids false positives on
    very short words).

    Works per-word for multi-word friends: compares first names independently.
    """
    candidate_lower = candidate.strip().lower()
    best_friend = None
    best_dist   = max_dist + 1

    for friend in friend_list:
        friend_lower = friend.lower()

        # Full-name comparison
        dist = _levenshtein(candidate_lower, friend_lower)
        threshold = max(max_dist, int(len(friend_lower) * 0.4))
        if dist <= threshold and dist < best_dist:
            best_dist   = dist
            best_friend = friend
            continue

        # First-name-only comparison (handles "Sowmya" vs "Sowmiya")
        first = friend_lower.split()[0]
        dist_first = _levenshtein(candidate_lower, first)
        threshold_first = max(max_dist, int(len(first) * 0.4))
        if dist_first <= threshold_first and dist_first < best_dist:
            best_dist   = dist_first
            best_friend = friend

    return best_friend if best_dist <= max_dist else None


def _semantic_match_friend(candidate: str, friend_list: list, threshold: float = 0.82) -> str | None:
    """
    spaCy vector similarity — only used when the candidate token actually
    HAS a meaningful vector (OOV proper nouns in en_core_web_sm have zero
    vectors and must not be compared, as they all collapse to the same
    meaningless cosine score).
    """
    if not friend_list:
        return None

    candidate_doc    = nlp(candidate.lower())
    candidate_tokens = [t for t in candidate_doc if t.has_vector and t.vector_norm > 0]
    if not candidate_tokens:
        return None                         # No real vectors → skip semantic

    best_friend, best_score = None, 0.0

    for friend in friend_list:
        friend_doc    = nlp(friend.lower())
        friend_tokens = [t for t in friend_doc if t.has_vector and t.vector_norm > 0]
        if not friend_tokens:
            continue

        scores    = [ct.similarity(ft) for ct in candidate_tokens for ft in friend_tokens]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        if avg_score > best_score:
            best_score  = avg_score
            best_friend = friend

    return best_friend if best_score >= threshold else None


# ---------------------------------------
# Person Extraction (case + edit-distance + semantic)
# ---------------------------------------
def _extract_person(doc, friend_list) -> tuple:
    """
    Returns (resolved_friend_name, raw_token_from_text).
    raw_token is the original word as it appeared in the text (may be misspelled).
    Both are used by _mask_person to fully sanitise the text.

    Matching priority:
      L0   — Direct token scan (exact, case-insensitive)
      L0.5 — Raw token edit-distance scan  ← catches misspellings early
      L1   — NER/PROPN exact match
      L2   — First-name exact match
      L3   — NER/PROPN edit-distance match
      L4   — Semantic vector similarity
      L5/6 — Self / pronoun → 'self'
      L7   — Default → 'self'
    """
    friend_set = {f.lower(): f for f in friend_list}

    # ── Collect NER + PROPN candidates ──────────────────────────────────────
    candidate_names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    temp_name = []
    for token in doc:
        if token.pos_ == "PROPN":
            temp_name.append(token.text)
        else:
            if temp_name:
                candidate_names.append(" ".join(temp_name))
                temp_name = []
    if temp_name:
        candidate_names.append(" ".join(temp_name))

    seen, unique_names = set(), []
    for n in candidate_names:
        if n.lower() not in seen:
            seen.add(n.lower())
            unique_names.append(n)

    # ── L0: Direct token exact match ────────────────────────────────────────
    for token in doc:
        if token.text.lower() in friend_set:
            return friend_set[token.text.lower()], token.text

    tokens = [t.text for t in doc]
    for i in range(len(tokens) - 1):
        bigram = (tokens[i] + " " + tokens[i + 1]).lower()
        if bigram in friend_set:
            return friend_set[bigram], tokens[i] + " " + tokens[i + 1]

    # ── L0.5: Raw token edit-distance (catches misspellings before NER) ──────
    for token in doc:
        word = token.text
        if not word.isalpha():
            continue
        if not (word[0].isupper() or token.pos_ == "PROPN"):
            continue
        matched = _edit_distance_match_friend(word, friend_list, max_dist=2)
        if matched:
            return matched, word          # raw_token = original misspelled word

    # ── L1: NER/PROPN exact match ────────────────────────────────────────────
    for name in unique_names:
        if name.lower() in friend_set:
            return friend_set[name.lower()], name

    # ── L2: First-name exact match ───────────────────────────────────────────
    for name in unique_names:
        first = name.split()[0].lower()
        if first in friend_set:
            return friend_set[first], name

    # ── L3: NER/PROPN edit-distance ──────────────────────────────────────────
    for name in unique_names:
        matched = _edit_distance_match_friend(name, friend_list, max_dist=2)
        if matched:
            return matched, name

    # ── L4: Semantic vector similarity ───────────────────────────────────────
    for name in unique_names:
        matched = _semantic_match_friend(name, friend_list)
        if matched:
            return matched, name

    # ── L5/6: Self / pronoun ─────────────────────────────────────────────────
    for token in doc:
        if token.text.lower() in SELF_WORDS:
            return "self", token.text

    for token in doc:
        if token.text.lower() in PRONOUNS:
            return "self", token.text

    return "self", None

# ---------------------------------------
# Confidence Scoring (improved)
# ---------------------------------------
def _score_confidence(action, location) -> float:
    score = 1.0
    if not action:
        score -= 0.3
    if not location:
        score -= 0.3
    return round(max(0.0, min(1.0, score)), 2)

# ---------------------------------------
# Person-masked text helper
# ---------------------------------------
def _mask_person(text: str, person: str, raw_token: str = None) -> str:
    """
    Remove the matched person name from text so downstream extractors never
    see it as a location or action fragment.

    Also strips `raw_token` (the original possibly-misspelled word) if it
    differs from the resolved person name — e.g. removes "Sowmya" even
    though the resolved name is "Sowmiya".
    """
    if not person or person == "self":
        return text

    cleaned = text

    # Remove  <prep> <PersonName>  pattern (resolved name)
    cleaned = re.sub(
        rf'\b(?:for|to|tell|notify|remind)\s+{re.escape(person)}\b',
        '', cleaned, flags=re.IGNORECASE
    )
    cleaned = re.sub(rf'\b{re.escape(person)}\b', '', cleaned, flags=re.IGNORECASE)

    # Also strip the original raw misspelled token if different
    if raw_token and raw_token.lower() != person.lower():
        cleaned = re.sub(
            rf'\b(?:for|to|tell|notify|remind)\s+{re.escape(raw_token)}\b',
            '', cleaned, flags=re.IGNORECASE
        )
        cleaned = re.sub(rf'\b{re.escape(raw_token)}\b', '', cleaned, flags=re.IGNORECASE)

    return re.sub(r'\s{2,}', ' ', cleaned).strip()


# ---------------------------------------
# Reminder Engine (person-first pipeline)
# ---------------------------------------
def reminder_engine(text: str, friend_list: list) -> dict:

    text_key = text.strip().lower()

    # Adaptive Memory Override
    if text_key in ADAPTIVE_MEMORY:
        return ADAPTIVE_MEMORY[text_key]

    doc = nlp(text)

    # ── Intent ────────────────────────────────────────────────────────────────
    if not _detect_intent(doc):
        return {"error": "Not a location-based reminder"}

    # ── Step 1: Resolve person FIRST ─────────────────────────────────────────
    person, raw_token = _extract_person(doc, friend_list)

    # ── Step 2: Mask person name + raw misspelled token, re-parse ────────────
    clean_text = _mask_person(text, person, raw_token)
    clean_doc  = nlp(clean_text)

    # ── Step 3: Extract action & location from sanitised text ─────────────────
    action   = _extract_action(clean_doc, clean_text)
    location = _extract_location(clean_doc, clean_text)

    # Spell-correct action
    if action:
        action = correct_action_text(action)

    # ── Confidence ────────────────────────────────────────────────────────────
    confidence = _score_confidence(action, location)

    return {
        "intent":     "location_based_reminder",
        "action":     action,
        "location":   location,
        "person":     person,
        "confidence": confidence,
    }

# ---------------------------------------
# Learning From User Correction (unchanged)
# ---------------------------------------
def learn_from_user_correction(original_text: str, corrected_output: dict):
    key = original_text.strip().lower()
    ADAPTIVE_MEMORY[key] = corrected_output
    save_memory(ADAPTIVE_MEMORY)